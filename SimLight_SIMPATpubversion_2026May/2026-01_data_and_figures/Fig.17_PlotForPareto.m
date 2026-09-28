clc; clear; close all;

% x Lat - y Pow
DiB_Lat=[3.837;3.856;3.838;3.832;3.837;3.835;5.578;5.58;5.572;5.568;5.575;5.586;5.069;5.065;5.065;5.071;5.078;5.071]
DiB_Pow=[51.706;83.86312;117.11722;146.67577;178.20447;210.15678;315.788;515.36741;711.65047;915.17972;1113.02949;1322.94786;969.218;1583.18955;2202.7231;2820.24753;3439.00779;4054.38372]

MhB_Lat=[4.867;4.563;4.353;4.254;4.147;4.144;8.142;7.387;6.906;6.629;6.487;6.308;7.952;7.135;6.614;6.299;6.063;5.922]
MhB_Pow=[45.16243;76.9513;107.91356;138.71859;170.89831;201.59109;265.74493;460.5583;657.4396;858.29513;1058.03119;1260.81841;816.8046;1413.54701;2019.02223;2643.17958;3245.62689;3862.23991]

%HyB_Pow=[53.13;84.352;115.115;148.924;179.57;210.326;321.718;516.75;710.44;916.373;1112.286;1320.732;984.444;1585.27;2176.596;2819.209;3423.75;4053.111]
%HyBLatMean
%3.791;4.033;3.943;3.918;3.893;3.89;5.503;6.001;5.789;5.782;5.702;5.691;4.977;5.479;5.258;5.234;5.163;5.156

Lat_HyB_Q_HP=[3.791;3.791;3.794;3.787;3.795;3.797;5.503;5.503;5.5;5.514;5.502;5.506;4.977;4.977;4.979;4.969;4.976;4.976]

Lat_HyB_Q_LP=[3.791;4.274;4.093;4.048;3.991;3.983;5.503;6.5;6.079;6.049;5.904;5.875;4.977;5.981;5.537;5.499;5.35;5.336]

Pow_HyB_Q_HP=[46.76;53.2;71.01026;85.19786;101.9371;116.44445;277.218;321.938;434.02278;522.21053;628.80483;725.32941;845.794;984.774;1329.45441;1611.34456;1938.6532;2224.67105]

Pow_HyB_Q_LP=[11.64;35.76454;48.69721;68.32555;82.32416;98.52342;53.74;206.71006;288.22994;405.71663;495.226;607.38414;149.22;619.27557;865.74999;1226.8597;1504.25075;1847.3209]

figure('Name', 'Pareto Plot Replication', 'Color', 'w');
hold on;
grid on;
box on;

%https://color.adobe.com/create/color-accessibility
%No conflicts found. Swatches are color blind safe for Deuteranopia, Protanopia, Tritanopia

DiB = plot(DiB_Lat, DiB_Pow, '^',...
           'Color', '#48FFB7', ...
           'MarkerFaceColor', '#48FFB7', ...
           'MarkerSize', 7);
MhB = plot(MhB_Lat, MhB_Pow, 's',...
           'Color', '#FA2AC0', ...
           'MarkerFaceColor', '#FA2AC0', ...
           'MarkerSize', 7);
HyB_QHP = plot(Lat_HyB_Q_HP, Pow_HyB_Q_HP, 'o', ...
    'Color', '#11B2ED', ...
    'MarkerFaceColor', '#11B2ED', ...
    'MarkerSize', 7);
HyB_QLP = plot(Lat_HyB_Q_LP, Pow_HyB_Q_LP, 'o', ...
    'Color', '#451EF5', ...
    'MarkerFaceColor', '#451EF5', ...
    'MarkerSize', 7);

xlim([3 8.5]);
ylim([0 4300]);

xlabel('Average latency (ms)', 'FontSize', 12);
ylabel('Power consumption (kW)', 'FontSize', 12);
%title('Pareto: Lat vs Pow, unlim λ, load 20-120G, wavcap 40G, splt 50-50', 'FontSize', 14, 'FontWeight', 'bold');

%xlim([2.6, 4.6]);
%ylim([3.05, 4.15]);

lg=legend([HyB_QHP, HyB_QLP, DiB, MhB], ...
       {'Hybrid Bypass Q_{HP}','Hybrid Bypass Q_{LP}', 'Direct Bypass', 'Multi-hop Bypass'}, ...
       'Location', 'northeast');

hold off;
set(lg, 'FontSize', 10);
%set(1, 'position', [200, 200, 1000, 750]);
drawnow;
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2\Pareto\Fig17Pareto.png', '-dpng', '-r300'); % 300 DPI
