import os
import pandas as pd
from sqlalchemy import create_engine
import sys

DB_FILENAME =  sys.argv[1]

base_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(base_dir, DB_FILENAME)

DB_CONNECTION_STR = f'sqlite:///{db_path}'

E_R = 1000.0   # Energy per Router (Er)
E_T = 73.0    # Energy per Transponder (Et)
E_E = 8.0     # Energy per Amplifier/EDFA (Ee)

wavelength_capacity = f"40.0"

class NetworkPowerCalculator:
    def __init__(self, db_conn_str):
        self.engine = create_engine(db_conn_str)

    def _get_queue_filter(self, queues):
        if isinstance(queues, int):
            return f"({queues})"
        return f"({','.join(map(str, queues))})"

    def calculate_power(self, queues):
        q_filter = self._get_queue_filter(queues)

        sql_delta = f"""
            SELECT 
                src as Node, 
                CEIL(SUM(cap) / {wavelength_capacity}) as Di
            FROM TrafficRequests
            WHERE result = 'Pass' AND quenum IN {q_filter}
            GROUP BY src
        """
        
        #print ("Di query:", sql_delta)

        sql_sigma = f"""
            SELECT 
                routeTReqOverVT_VLsrc as Node, 
                COUNT(DISTINCT CONCAT(routeTReqOverVT_VLsrc, '_', routeTReqOverVT_VLdst, '_', routeTReqOverVT_VLnum)) as Sigma_Cij
            FROM route_traffic_requests_over_virtual_and_physical_topology
            WHERE TReqQueNum IN {q_filter}
            and routeTReqOverVTtype = "New"
            GROUP BY routeTReqOverVT_VLsrc
        """
        
        #print ("Cij query:", sql_sigma)

        df_delta = pd.read_sql(sql_delta, self.engine)
        df_sigma = pd.read_sql(sql_sigma, self.engine)

        df_term1 = pd.merge(df_delta, df_sigma, on='Node', how='outer').fillna(0)
        
        term1_total = (E_R * (df_term1['Di'] + df_term1['Sigma_Cij'])).sum()

        sql_w_mn = f"""
            SELECT 
                routeVLoverPT_PLsrc as PL_Source_Node,
                routeVLoverPT_PLdst as PL_Dest_Node,
                routeVLoverPT_fiberID as Fiber_ID,
                COUNT(DISTINCT routeVLoverPT_waveID) as w_mn
            FROM route_traffic_requests_over_virtual_and_physical_topology
            WHERE TReqQueNum IN {q_filter}
            and routeTReqOverVTtype = "New"
            GROUP BY routeVLoverPT_PLsrc, routeVLoverPT_PLdst, routeVLoverPT_fiberID
        """
        
        #print ("w_mn query:", sql_w_mn)

        df_w = pd.read_sql(sql_w_mn, self.engine)
        
        term2_total = (E_T * df_w['w_mn']).sum()

        sql_a_mn = """
            SELECT 
                src as PL_Source_Node, 
                dst as PL_Dest_Node, 
                (LatEDFAs / 0.1 * 2) as Amn
            FROM PhysicalLinks
        """
        
        #print ("A_mn query:", sql_a_mn)

        sql_f_mn = f"""
            SELECT 
                routeVLoverPT_PLsrc as PL_Source_Node,
                routeVLoverPT_PLdst as PL_Dest_Node,
                COUNT(DISTINCT routeVLoverPT_fiberID) * 2 as f_mn
            FROM route_traffic_requests_over_virtual_and_physical_topology
            WHERE TReqQueNum IN {q_filter}
            and routeTReqOverVTtype = "New"
            GROUP BY routeVLoverPT_PLsrc, routeVLoverPT_PLdst
        """
        
        #print ("f_mn query:", sql_f_mn)

        df_a = pd.read_sql(sql_a_mn, self.engine)
        df_f = pd.read_sql(sql_f_mn, self.engine)

        df_term3 = pd.merge(df_f, df_a, on=['PL_Source_Node', 'PL_Dest_Node'], how='inner')
        
        term3_total = (E_E * df_term3['Amn'] * df_term3['f_mn']).sum()

        total_energy = term1_total + term2_total + term3_total
        return total_energy

# main
if __name__ == "__main__":
    try:
        # Initialize Calculator
        calc = NetworkPowerCalculator(DB_CONNECTION_STR)
        
        #print("*** Power ***")
        
        print(f"filename",end=";")
        print(f"(a) Total Power (All Queues)",end=";")
        print(f"(b) Power for Queue HP",end=";")
        print(f"(c) Power for Queue LP")

        print(sys.argv[1],end=";")

        total_pwr = calc.calculate_power(queues=[0, 1])

        print(f"{total_pwr:,.3f}",end=";")

        q0_pwr = calc.calculate_power(queues=[0])
        
        print(f"{q0_pwr:,.3f}",end=";")

        q1_pwr = calc.calculate_power(queues=[1])
        
        print(f"{q1_pwr:,.3f}")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        print("Ensure your database connection string is correct and tables exist.")


