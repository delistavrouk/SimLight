close all; clear; clc;
%graphics_toolkit('gnuplot')
%graphics_toolkit('qt')
%graphics_toolkit('fltk')

%figure('position', [100, 100, 800, 700])  % Larger figure = finer detail
%set(gca, 'FontSize', 14, 'LineWidth', 0.6)

x = [1, 2, 3, 4, 5, 6];

PowNSFnetDirect = [315.788;515.367;711.65;915.18;1113.029;1322.948];
ciPowNSFnetDirect = [0.418;2.928;4.605;6.751;7.325;9.162];

%PowNSFnetHybridBypassNoRevisits = [321.718;516.75;710.44;916.373;1112.286;1320.732];
%ciPowNSFnetHybridBypassNoRevisits = [0.301;2.304;3.179;4.452;4.834;6.49];

PowNSFnetHybridBypassQHP   = [277.218	321.938	434.02278	522.21053	628.80483	725.32941]
ciPowNSFnetHybridBypassQHP = [0.286077493	0.703962863	2.349163676	2.906015383	3.728623277	4.294591129]

PowNSFnetHybridBypassQLP = [53.74	206.71006	288.22994	405.71663	495.226	607.38414]
ciPowNSFnetHybridBypassQLP = [0.305863141	1.931671298	2.565172311	3.407091109	3.53024061	4.702876804]

PowNSFnetMultihop = [265.745;460.558;657.44;858.295;1058.031;1260.818];
ciPowNSFnetMultihop = [0.908;2.346;4.223;5.847;7.224;8.717];


Direct1Q      = PowNSFnetDirect
ciDirect1Q    = ciPowNSFnetDirect
HybridQHP2Q   = PowNSFnetHybridBypassQHP
ciHybridQHP2Q = ciPowNSFnetHybridBypassQHP
HybridQLP2Q   = PowNSFnetHybridBypassQLP
ciHybridQLP2Q = ciPowNSFnetHybridBypassQLP
Multihop1Q    = PowNSFnetMultihop
ciMultihop1Q  = ciPowNSFnetMultihop

labels = {'20','40','60','80','100','120'};

box on
grid on
hold on;

% Helper that returns the handle of the main plotted line (for the legend)
function h = errorTbar(x, y, ci, style, cap, color)
  if nargin < 6, color = 'k'; end
  %h = plot(x, y, style, 'LineWidth', 0.9, 'MarkerSize', 9, 'MarkerFaceColor', 'w', 'Color', color);
  h = plot(x, y, style, 'MarkerSize', 9, 'MarkerFaceColor', 'w', 'Color', color);
  for i = 1:numel(x)
    % vertical bar
    %line([x(i) x(i)], [y(i)-ci(i), y(i)+ci(i)], 'Color', color, 'LineWidth', 1);
    line([x(i) x(i)], [y(i)-ci(i), y(i)+ci(i)], 'Color', color);
    % caps
    %line([x(i)-cap x(i)+cap], [y(i)+ci(i) y(i)+ci(i)], 'Color', color, 'LineWidth', 1);
    %line([x(i)-cap x(i)+cap], [y(i)-ci(i) y(i)-ci(i)], 'Color', color, 'LineWidth', 1);
    line([x(i)-cap x(i)+cap], [y(i)+ci(i) y(i)+ci(i)], 'Color', color);
    line([x(i)-cap x(i)+cap], [y(i)-ci(i) y(i)-ci(i)], 'Color', color);
  end
end

% nice cap width proportional to x spacing
cap = 0.09 * mean(diff(x));

% Plot all four and keep the main line handles
h1 = errorTbar(x, Direct1Q,    ciDirect1Q,    'o--', cap, [0 0 0]);
h2 = errorTbar(x, Multihop1Q,  ciMultihop1Q,  's:',  cap, [0 0 0]);
h3 = errorTbar(x, HybridQHP2Q, ciHybridQHP2Q, 'd-',  cap, [0 0 0]);
h4 = errorTbar(x, HybridQLP2Q, ciHybridQLP2Q, '^-',  cap, [0 0 0]);



xlim([1 6]);
%ylim([0 220]);
set(gca, 'XTick', x);
set(gca, 'XTickLabel', labels);

set(gca, 'YMinorTick', 'on');
set(gca, 'YGrid', 'on');
set(gca, 'YMinorGrid', 'on');
grid on;

%title('NSFnet');

xlabel('Traffic demand (Gbps / node pair)');
ylabel('Power consumption (kW)');

% Use the line handles so the legend shows the right markers
lg=legend([h1 h2 h3 h4], ...
  {'Direct Bypass: single Q', ...
   'Multi-hop Bypass: single Q', ...
   'Hybrid Bypass: Q_{HP}', ...
   'Hybrid Bypass: Q_{LP}'}, ...
   'Location', 'northwest');

hold off;

set(lg, 'FontSize', 10);
%set(1, 'position', [200, 200, 1000, 750]);
drawnow;
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2\Pareto\Fig16b.png', '-dpng', '-r300'); % 300 DPI
