#import openpyxl
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
import hashlib 
import ast


class Spreadsheet:
    # class to handle exporting network topology and routing dictionaries to a multi-sheet Microsoft Excel workbook.

    def __init__(self):
        self.wb = Workbook()
        
        # Pre-define reusable styles
        self.header_fill = PatternFill(start_color="2F5597", end_color="2F5597", fill_type="solid")
        self.header_font = Font(color="FFFFFF", bold=True)
        self.center_aligned = Alignment(horizontal="center", vertical="center", wrap_text=True)
        self.left_aligned = Alignment(horizontal="left", vertical="center")
        self.thin_border = Border(left=Side(style='thin'), right=Side(style='thin'), 
                                  top=Side(style='thin'), bottom=Side(style='thin'))

    def save(self, filename):
        self.wb.save(filename)
    

    def _get_or_create_sheet(self, sheet_name):
        if "Sheet" in self.wb.sheetnames and len(self.wb.sheetnames) == 1:
            ws = self.wb["Sheet"]
            if ws.max_row == 1 and ws.max_column == 1 and ws.cell(1,1).value is None:
                ws.title = sheet_name
                return ws
        return self.wb.create_sheet(title=sheet_name)

    def _apply_styling(self, ws, start_row, start_col, end_row, end_col, is_header=False):
        for r in range(start_row, end_row + 1):
            for c in range(start_col, end_col + 1):
                cell = ws.cell(row=r, column=c)
                cell.alignment = self.center_aligned
                cell.border = self.thin_border
                if is_header:
                    cell.fill = self.header_fill
                    cell.font = self.header_font


    def export_vt_dictionary(self, data_dict, sheet_name="VT"):
        ws = self._get_or_create_sheet(sheet_name)

        if len(data_dict) > 0:
            longestvalue = len(max(data_dict.values(), key=len))
            total_cols = longestvalue + 1
            
            ws.cell(row=1, column=1, value="Source")
            ws.cell(row=1, column=2, value="Destinations")
            if longestvalue > 1:
                ws.merge_cells(start_row=1, start_column=2, end_row=1, end_column=total_cols)
                
            self._apply_styling(ws, 1, 1, 1, total_cols, is_header=True)

            current_row = 2
            for key, values in data_dict.items():
                ws.cell(row=current_row, column=1, value=str(key))
                for col_idx, data in enumerate(values, start=2):
                    ws.cell(row=current_row, column=col_idx, value=str(data))
                    
                self._apply_styling(ws, current_row, 1, current_row, total_cols)
                current_row += 1

            ws.column_dimensions['A'].width = 15
            for col_idx in range(2, total_cols + 1):
                ws.column_dimensions[get_column_letter(col_idx)].width = 15
        else:
            ws.append(["∅ Empty"])

    def export_request_routing_info(self, data_dict, sheet_name="VLperTR"):
        ws = self._get_or_create_sheet(sheet_name)

        if len(data_dict) > 0:
            headers = ["Queue", "Request", "(Virtual link (s,d,n), type, cap utilised, step, step seq no)"]
            ws.append(headers)
            self._apply_styling(ws, 1, 1, 1, 3, is_header=True)

            current_row = 2
            for key, values in data_dict.items():
                start_row = current_row
                ws.cell(row=start_row, column=1, value=key[0])
                ws.cell(row=start_row, column=2, value=key[1])
                
                for value in values:
                    ws.cell(row=current_row, column=3, value=str(value)).alignment = self.left_aligned
                    ws.cell(row=current_row, column=3).border = self.thin_border
                    current_row += 1
                
                if current_row - start_row > 1:
                    ws.merge_cells(start_row=start_row, start_column=1, end_row=current_row-1, end_column=1)
                    ws.merge_cells(start_row=start_row, start_column=2, end_row=current_row-1, end_column=2)
                
                self._apply_styling(ws, start_row, 1, current_row-1, 2)

            ws.column_dimensions['A'].width = 10
            ws.column_dimensions['B'].width = 10
            ws.column_dimensions['C'].width = 80
        else:
            ws.append(["∅ Empty"])

    def export_vl_ids(self, data_dict, sheet_name="VLIDs"):
        ws = self._get_or_create_sheet(sheet_name)

        if len(data_dict) > 0:
            longestvalue = len(max(data_dict.values(), key=len))
            total_cols = longestvalue + 2

            ws.cell(row=1, column=1, value="virtual link src,dst")
            ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=2)
            
            ws.cell(row=1, column=3, value="ID numbers")
            ws.merge_cells(start_row=1, start_column=3, end_row=2, end_column=total_cols)

            ws.cell(row=2, column=1, value="source (s)")
            ws.cell(row=2, column=2, value="destination (d)")
            
            self._apply_styling(ws, 1, 1, 2, total_cols, is_header=True)

            current_row = 3
            for key, values in data_dict.items():
                ws.cell(row=current_row, column=1, value=key[0])
                ws.cell(row=current_row, column=2, value=key[1])
                for col_idx, data in enumerate(values, start=3):
                    ws.cell(row=current_row, column=col_idx, value=data)
                
                self._apply_styling(ws, current_row, 1, current_row, total_cols)
                current_row += 1
                
            for col_idx in range(1, total_cols + 1):
                ws.column_dimensions[get_column_letter(col_idx)].width = 18
        else:
            ws.append(["∅ Empty"])

    def export_vl_traffic_reqs(self, data_dict, sheet_name="TRperVL"):
        ws = self._get_or_create_sheet(sheet_name)

        if len(data_dict) > 0:
            ws.cell(row=1, column=1, value="Routing of Traffic Requests over Virtual Links")
            ws.merge_cells("A1:G1")
            
            desc = "{(Virtual Link):[(Traffic Request 1, ...)], ...}\n{(source, destination, number): [(queue, request, capacity required, type), ...]}"
            ws.cell(row=2, column=1, value=desc)
            ws.merge_cells("A2:G2")
            ws.row_dimensions[2].height = 30
            
            ws.cell(row=3, column=1, value="Virtual Link")
            ws.merge_cells("A3:C3")
            ws.cell(row=3, column=4, value="Traffic Request")
            ws.merge_cells("D3:G3")
            
            headers = ["source", "destination", "number", "queue", "request", "capacity required", "type"]
            for col, val in enumerate(headers, 1):
                ws.cell(row=4, column=col, value=val)

            self._apply_styling(ws, 1, 1, 4, 7, is_header=True)

            current_row = 5
            for key, values in data_dict.items():
                start_row = current_row
                ws.cell(row=start_row, column=1, value=key[0])
                ws.cell(row=start_row, column=2, value=key[1])
                ws.cell(row=start_row, column=3, value=key[2])
                
                for val in values:
                    ws.cell(row=current_row, column=4, value=val[0])
                    ws.cell(row=current_row, column=5, value=val[1])
                    ws.cell(row=current_row, column=6, value=float(f"{val[2]:.3f}"))
                    ws.cell(row=current_row, column=7, value=val[3])
                    current_row += 1
                
                if current_row - start_row > 1:
                    ws.merge_cells(start_row=start_row, start_column=1, end_row=current_row-1, end_column=1)
                    ws.merge_cells(start_row=start_row, start_column=2, end_row=current_row-1, end_column=2)
                    ws.merge_cells(start_row=start_row, start_column=3, end_row=current_row-1, end_column=3)
                
                self._apply_styling(ws, start_row, 1, current_row-1, 7)
                
            for col_idx in range(1, 8):
                ws.column_dimensions[get_column_letter(col_idx)].width = 18
        else:
            ws.append(["∅ Empty"])

    def export_vl_totals(self, data_dict, sheet_name="VLtotals"):
        ws = self._get_or_create_sheet(sheet_name)

        if len(data_dict) > 0:
            ws.cell(row=1, column=1, value="virtual link src,dst")
            ws.merge_cells("A1:C1")
            ws.cell(row=1, column=4, value="cap utilised, cap free, num of traffic requests")
            ws.merge_cells("D1:F2")
            
            ws.cell(row=2, column=1, value="source (s)")
            ws.cell(row=2, column=2, value="destination (d)")
            ws.cell(row=2, column=3, value="number (n)")

            self._apply_styling(ws, 1, 1, 2, 6, is_header=True)

            current_row = 3
            for key, values in data_dict.items():
                ws.cell(row=current_row, column=1, value=key[0])
                ws.cell(row=current_row, column=2, value=key[1])
                ws.cell(row=current_row, column=3, value=key[2])
                
                for col_idx, data in enumerate(values, start=4):
                    ws.cell(row=current_row, column=col_idx, value=float(f"{data:.3f}"))
                    
                self._apply_styling(ws, current_row, 1, current_row, 6)
                current_row += 1
                
            for col_idx in range(1, 7):
                ws.column_dimensions[get_column_letter(col_idx)].width = 18
        else:
            ws.append(["∅ Empty"])

    

    def _get_excel_pastel_color(self, identifier):
        hash_object = hashlib.md5(str(identifier).encode())
        hex_color = hash_object.hexdigest()[:6]
        
        r = (int(hex_color[0:2], 16) + 255) // 2
        g = (int(hex_color[2:4], 16) + 255) // 2
        b = (int(hex_color[4:6], 16) + 255) // 2
        
        # openpyxl requires an 8-character hex string (FF for full opacity)
        return f"FF{r:02x}{g:02x}{b:02x}".upper()

    def _parse_lightpath_identifier(self, lp):
        if isinstance(lp, tuple) or isinstance(lp, list):
            return lp[0], lp[1], lp[2]
        
        # Fallback if lp is a string representation of a tuple, e.g., "('A', 'B', 1)"
        try:
            parsed = ast.literal_eval(str(lp))
            return parsed[0], parsed[1], parsed[2]
        except (ValueError, SyntaxError):
            # Absolute fallback if it's just a raw string
            return str(lp), "N/A", "N/A"


    def export_reservations(self, links, link_list, sheet_name="WAs"):
        ws = self._get_or_create_sheet(sheet_name)
        
        # Title
        ws.cell(row=1, column=1, value="Current Network Reservations Map").font = Font(bold=True, size=14)
        current_row = 3
        
        max_slots = max([len(fiber) for link_fibers in links for fiber in link_fibers], default=0)

        for i, link in enumerate(link_list):
            # Link Header
            ws.cell(row=current_row, column=1, value=f"Link {link} (link id:{i})").font = Font(bold=True)
            current_row += 1
            
            start_table_row = current_row
            
            for fiber_idx, fiber in enumerate(links[i]):
                ws.cell(row=current_row, column=1, value=f"Fiber {fiber_idx}").border = self.thin_border
                
                for slot_idx, slot in enumerate(fiber):
                    col = slot_idx + 2
                    cell = ws.cell(row=current_row, column=col)
                    cell.border = self.thin_border
                    cell.alignment = self.center_aligned
                    
                    if slot == '':
                        cell.value = "∅"
                    else:
                        cell.value = str(slot)
                        # Apply unique generated color
                        color_hex = self._get_excel_pastel_color(slot)
                        cell.fill = PatternFill(start_color=color_hex, end_color=color_hex, fill_type="solid")
                        
                current_row += 1
                
            # Formatting table bounds
            self._apply_styling(ws, start_table_row, 1, current_row - 1, max_slots + 1)
            current_row += 1 # Add an empty row between link tables

        # Adjust column widths
        ws.column_dimensions['A'].width = 25
        for col in range(2, max_slots + 2):
            ws.column_dimensions[get_column_letter(col)].width = 15


    def export_lightpath_routes(self, links, link_list, sheet_name="WAperLP"):
        ws = self._get_or_create_sheet(sheet_name)
        
        lightpaths = {}
        
        for i, link in enumerate(link_list):
            for fiber_idx, fiber in enumerate(links[i]):
                for wave_idx, slot in enumerate(fiber):
                    if slot != '':
                        if slot not in lightpaths:
                            lightpaths[slot] = []
                        src, dst = link
                        lightpaths[slot].append({
                            'src': src, 'dst': dst, 'fiber': fiber_idx, 'channel': wave_idx
                        })

        if not lightpaths:
            ws.append(["No active lightpaths found."])
            return

        ws.cell(row=1, column=1, value="Lightpath (Source, Dest, ID)")
        ws.merge_cells("A1:C1")
        ws.cell(row=1, column=4, value="Wavelength ID (Source, Dest, Fiber, Channel)")
        ws.merge_cells("D1:G1")
        self._apply_styling(ws, 1, 1, 1, 7, is_header=True)

        current_row = 2
        for lp, path in lightpaths.items():
            start_row = current_row
            n_hops = len(path)
            
            # Generate row color and parse the LP ID tuple
            color_hex = self._get_excel_pastel_color(lp)
            row_fill = PatternFill(start_color=color_hex, end_color=color_hex, fill_type="solid")
            lp_src, lp_dst, lp_id = self._parse_lightpath_identifier(lp)
            
            for hop in path:
                # Write LP Base Info (Merged visually later)
                ws.cell(row=current_row, column=1, value=str(lp_src)).font = Font(bold=True)
                ws.cell(row=current_row, column=2, value=str(lp_dst)).font = Font(bold=True)
                ws.cell(row=current_row, column=3, value=str(lp_id)).font = Font(bold=True)
                
                # Write Hop Details
                ws.cell(row=current_row, column=4, value=str(hop['src']))
                ws.cell(row=current_row, column=5, value=str(hop['dst']))
                ws.cell(row=current_row, column=6, value=hop['fiber'])
                ws.cell(row=current_row, column=7, value=hop['channel'])
                
                # Apply fill color to the entire row
                for col in range(1, 8):
                    ws.cell(row=current_row, column=col).fill = row_fill
                    
                current_row += 1
            
            # Merge the lightpath identifier columns for the duration of the hops
            if n_hops > 1:
                ws.merge_cells(start_row=start_row, start_column=1, end_row=current_row-1, end_column=1)
                ws.merge_cells(start_row=start_row, start_column=2, end_row=current_row-1, end_column=2)
                ws.merge_cells(start_row=start_row, start_column=3, end_row=current_row-1, end_column=3)
                
            self._apply_styling(ws, start_row, 1, current_row-1, 7)

        # Auto-adjust column widths
        for col_idx in range(1, 8):
            ws.column_dimensions[get_column_letter(col_idx)].width = 15





    #21-7-2026 addition of function for exporting to Excel spreadsaheet
    def _export_generic_data(self, sheet_name, headers, data_rows):
        """
        A private helper method to handle the repetitive tasks of creating/clearing 
        a worksheet, writing headers, applying basic formatting, and writing data rows.
        """
        # Create or clear the sheet
        if sheet_name in self.wb.sheetnames:
            ws = self.wb[sheet_name]
            ws.delete_rows(1, ws.max_row)
        else:
            ws = self.wb.create_sheet(title=sheet_name)

        # Write and style headers
        ws.append(headers)
        for col_num, cell in enumerate(ws[1], 1):
            cell.font = Font(bold=True)
            cell.fill = PatternFill(start_color="D3D3D3", end_color="D3D3D3", fill_type="solid")
            cell.border = Border(bottom=Side(style='thin'))

        # Write data rows
        for row in data_rows:
            # Ensure row is a list/tuple to append properly
            ws.append(list(row))

        # Auto-adjust column widths for readability
        for col in ws.columns:
            max_length = 0
            column_letter = col[0].column_letter
            for cell in col:
                try:
                    if cell.value and len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = (max_length + 2)
            ws.column_dimensions[column_letter].width = adjusted_width


    def export_network_nodes(self, data_rows):
        headers = ["Node Num", "Name"]
        self._export_generic_data("Nodes", headers, data_rows)

    def export_network_links(self, data_rows):
        headers = ["Source", "Destination", "Distance", "LatEDFAs", "LatFibLen"]
        self._export_generic_data("PhysicalLinks", headers, data_rows)

    def export_queues(self, data_rows):
        headers = ["Queue Num", "Name"]
        self._export_generic_data("Queues", headers, data_rows)

    def export_traffic_requests(self, data_rows):
        headers = ["Queue Num", "Req Num", "Source", "Destination", "Capacity (Gbps)", "Result"]
        self._export_generic_data("TReqs", headers, data_rows)

    def export_virtual_links(self, data_rows):
        headers = ["Source", "Destination", "Num", "Cap Utilized", "Cap Free", "Result Tag"]
        self._export_generic_data("Virtual Links", headers, data_rows)

    def export_run_configuration(self, data_rows):
        # Assuming data_rows is a list of tuples like: [("Parameter", "Value"), ...]
        headers = ["argument", "explanation", "value"]
        self._export_generic_data("RunConfiguration", headers, data_rows)

    def export_run_ID(self, data_rows):
        headers = ["UUID"]
        self._export_generic_data("RunID", headers, data_rows)

    def export_routing_vl_over_pt(self, data_rows):
        headers = [
            "VL Src", "VL Dst", "VL Num", "PL Src", "PL Dst", 
            "Fiber ID", "Wave ID", "Type", "wavelength (Hop) sequence number", "Number of wavelengths (Hops)", 
            "Shortest Path (Int)", "Shortest Path (Str)", 
            "PL Direction", "PL Current Src", "PL Current Dst", 
            "Lat IP", "Lat Transp", "Result"
        ]
        self._export_generic_data("routingVLoverPT_onlyPass", headers, data_rows)

    def export_routing_tr_over_vt(self, data_rows):
        headers = [
            "Req Queue Num", "Req Num", "VL Src", "VL Dst", "VL Num", 
            "Util Cap", "Free Cap", "Type", "Routing Step (thread)", 
            "Rout Step (thread) VL Seq Num", "Result"
        ]
        self._export_generic_data("routingTRoverVT", headers, data_rows)

    def export_latency_of_traffic_request(self, data_rows):
        headers = ["TReq Queue Num", "TReq Num", "Traffic Request Latency"]
        self._export_generic_data("LatencyOfTReq", headers, data_rows)

    def export_latency_of_thread_of_traffic_request(self, data_rows):
        # Adjust headers based on your specific SQLite schema for this table
        headers = ["TReq Queue Num", "TReq Num", "routeTReqOverVTroutingStep (ThreadID)", "NumberOfLightpathHops","LatIP", 
                   "LatTransponder", "LatEDFA","LatFibLength(Propagation)", "ThreadLatency"
        ]
        self._export_generic_data("LatencyOfThreadsOfTReqs", headers, data_rows)

    def export_route_tr_over_vt_and_pt(self, data_rows): 
        headers = [ "TReqQueNum", "TReqReqNum", "TReqSrc", "TReqDst", "TReqCap", "TReqResult", "VLsrc", "VLdst",
                    "VLnum", "VLcaputil", "VLcapfree", "VLresult", "routeTReqOverVTtype", "routeTReqOverVTroutingStep",
                    "routeTReqOverVTroutStepVLseqnum", "routeTReqOverVTresult", "routeVLoverPT_PLsrc",
                    "routeVLoverPT_PLdst", "routeVLoverPT_fiberID", "routeVLoverPT_waveID", "routeVLoverPT_type",
                    "routeVLoverPT_HopSeqNum", "routeVLoverPT_NumOfHops",
                    "routeVLoverPT_shPathAsInt", "routeVLoverPT_shPathAsStr",
                    "routeVLoverPT_PLdir", "routeVLoverPT_currSrc", "routeVLoverPT_currDest", "routeVLoverPT_LatIP",
                    "routeVLoverPT_LatTransp",	"routeVLoverPT_result",	"PLdistance",	"PLlatEDFA", 	"PLlatFibLen"
        ]
        self._export_generic_data("routeTRoverVTandPT", headers, data_rows)



