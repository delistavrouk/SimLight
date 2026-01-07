close all; clear; clc;
%graphics_toolkit('gnuplot')
%graphics_toolkit('qt')
%graphics_toolkit('fltk')

%figure('position', [100, 100, 800, 700])  % Larger figure = finer detail
%set(gca, 'FontSize', 14, 'LineWidth', 0.6)

x = [1, 2, 3, 4, 5, 6];

PowSTnetDirect = [51.706;83.863;117.117;146.676;178.204;210.157];
ciPowSTnetDirect = [0.166;1.087;1.717;2.496;2.846;3.901];

%PowSTnetHybridBypassNoRevisits = [53.13;84.352;115.115;148.924;179.57;210.326];
%ciPowSTnetHybridBypassNoRevisits = [0.069;0.893;1.327;1.737;2.07;2.545];

PowSTnetHybridBypassQHP   = [46.76	53.2	71.01026	85.19786	101.9371	116.44445]
ciPowSTnetHybridBypassQHP = [0.1225914	0.26958781	0.806928217	1.228940194	1.47013654	1.805043379]

PowSTnetHybridBypassQLP = [11.64	35.76454	48.69721	68.32555	82.32416	98.52342]
ciPowSTnetHybridBypassQLP = [0.111104696	0.813293093	1.023932835	1.39847832	1.525615285	1.817890981]

PowSTnetMultihop = [45.162;76.951;107.914;138.719;170.898;201.591];
ciPowSTnetMultihop = [0.308;1.06;1.626;2.087;3.178;4.133];

Direct1Q      = PowSTnetDirect
ciDirect1Q    = ciPowSTnetDirect
HybridQHP2Q   = PowSTnetHybridBypassQHP
ciHybridQHP2Q = ciPowSTnetHybridBypassQHP
HybridQLP2Q   = PowSTnetHybridBypassQLP
ciHybridQLP2Q = ciPowSTnetHybridBypassQLP
Multihop1Q    = PowSTnetMultihop
ciMultihop1Q  = ciPowSTnetMultihop

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
ylim([0 220]);
set(gca, 'XTick', x);
set(gca, 'XTickLabel', labels);

set(gca, 'YMinorTick', 'on');
set(gca, 'YGrid', 'on');
set(gca, 'YMinorGrid', 'on');
grid on;

%title('STnet');

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
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2\Pareto\Fig16a.png', '-dpng', '-r300'); % 300 DPI
