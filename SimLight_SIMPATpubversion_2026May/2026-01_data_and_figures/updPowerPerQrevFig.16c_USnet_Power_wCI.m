close all; clear; clc;
%graphics_toolkit('gnuplot')
%graphics_toolkit('qt')
%graphics_toolkit('fltk')

%figure('position', [100, 100, 800, 700])  % Larger figure = finer detail
%set(gca, 'FontSize', 14, 'LineWidth', 0.6)

x = [1, 2, 3, 4, 5, 6];

PowUSnetDirect = [969.218;1583.19;2202.723;2820.248;3439.008;4054.384];
ciPowUSnetDirect = [0.655;4.267;8.717;10.663;13.902;16.612];

%PowUSnetHybridBypassNoRevisits = [984.444;1585.27;2176.596;2819.209;3423.75;4053.111];
%ciPowUSnetHybridBypassNoRevisits = [0.527;4.293;5.672;8.195;11.789;12.786];

PowUSnetHybridBypassQHP   = [845.794	984.774	1329.45441	1611.34456	1938.6532	2224.67105]
ciPowUSnetHybridBypassQHP = [0.449875198	1.074840146	4.073889629	5.336480287	8.424770653	8.738497512]

PowUSnetHybridBypassQLP = [149.22	619.27557	865.74999	1226.8597	1504.25075	1847.3209]
ciPowUSnetHybridBypassQLP = [0.456130196	3.89259534	4.3462989	6.092387476	7.224314848	8.450798348]

PowUSnetMultihop = [816.805;1413.547;2019.022;2643.18;3245.627;3862.24];
ciPowUSnetMultihop = [1.441;3.659;7.304;10.028;15.839;17.55];

Direct1Q      = PowUSnetDirect
ciDirect1Q    = ciPowUSnetDirect
HybridQHP2Q   = PowUSnetHybridBypassQHP
ciHybridQHP2Q = ciPowUSnetHybridBypassQHP
HybridQLP2Q   = PowUSnetHybridBypassQLP
ciHybridQLP2Q = ciPowUSnetHybridBypassQLP
Multihop1Q    = PowUSnetMultihop
ciMultihop1Q  = ciPowUSnetMultihop

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
ylim([0 4300]);
set(gca, 'XTick', x);
set(gca, 'XTickLabel', labels);

set(gca, 'YMinorTick', 'on');
set(gca, 'YGrid', 'on');
set(gca, 'YMinorGrid', 'on');
grid on;

%title('USnet');

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
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2\Pareto\Fig16c.png', '-dpng', '-r300'); % 300 DPI
