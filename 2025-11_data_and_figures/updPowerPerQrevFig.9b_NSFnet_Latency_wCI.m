box on;
grid on;
close all; clf; clear; clc;

x = [1, 2, 3, 4, 5, 6];

labels = {'20','40','60','80','100','120'};

%box on
%grid on
hold on;

LatNSFnetDirect = [5.578;5.58;5.572;5.568;5.575;5.586];
ciLatNSFnetDirect = [0;0.01;0.014;0.014;0.016;0.015];
LatNSFnetMultihop = [8.142;7.387;6.906;6.629;6.487;6.308];
ciLatNSFnetMultihop = [0.048;0.052;0.04;0.04;0.035;0.031];

%LatNSFnetHybridBypassNoRevisits = [5.503;6.001;5.789;5.782;5.702;5.691];
%ciLatNSFnetHybridBypassNoRevisits = [0;0.02;0.017;0.017;0.014;0.013];
%LatNSFnetHybridBypassNoRevisitsQhp = [5.503;5.503;5.5;5.514;5.502;5.506];
%ciLatNSFnetHybridBypassNoRevisitsQhp = [0;0;0.013;0.014;0.016;0.015];

LatNSFnetHyByQHP = [5.503	5.503	5.49989	5.51376	5.50194	5.50594]
ciLatNSFnetHyByQHP = [1.41697E-15	1.41697E-15	0.013433416	0.014167508	0.01565707	0.015076141]

LatNSFnetHyByQLP = [5.503	6.49965	6.07867	6.04864	5.90382	5.87512]
ciLatNSFnetHyByQLP = [1.41697E-15	0.040637085	0.030554391	0.028881693	0.023390417	0.020193084]

Direct1Q      = LatNSFnetDirect
ciDirect1Q    = ciLatNSFnetDirect
Multihop1Q    = LatNSFnetMultihop
ciMultihop1Q  = ciLatNSFnetMultihop
HyByQHP       = LatNSFnetHyByQHP
ciHyByQHP     = ciLatNSFnetHyByQHP
HyByQLP       = LatNSFnetHyByQLP
ciHyByQLP     = ciLatNSFnetHyByQLP

% Helper that returns the handle of the main plotted line (for the legend)
function h = errorTbar(x, y, ci, style, cap, color)
  if nargin < 6, color = 'k'; end
  h = plot(x, y, style, 'MarkerSize', 10, 'MarkerFaceColor', 'w', 'Color', color);
  for i = 1:numel(x)
    % vertical bar
    line([x(i) x(i)], [y(i)-ci(i), y(i)+ci(i)], 'Color', color);
    % caps
    line([x(i)-cap x(i)+cap], [y(i)+ci(i) y(i)+ci(i)], 'Color', color);
    line([x(i)-cap x(i)+cap], [y(i)-ci(i) y(i)-ci(i)], 'Color', color);
  end
end

% nice cap width proportional to x spacing
cap = 0.06 * mean(diff(x));
% Plot all four and keep the main line handles
h1 = errorTbar(x, Multihop1Q, ciMultihop1Q, 'o:',  cap, [0 0 0]);
h2 = errorTbar(x, Direct1Q,   ciDirect1Q,   'd--', cap, [0 0 0]);
h4 = errorTbar(x, HyByQHP,    ciHyByQHP,    '*-',  cap, [0 0 0]);
h3 = errorTbar(x, HyByQLP,    ciHyByQLP,    's-',  cap, [0 0 0]);

xlim([1 6]);
%ylim([3.7 5]);
set(gca, 'XTick', x);
set(gca, 'XTickLabel', labels);
set(gca, 'YMinorTick', 'on');
set(gca, 'YGrid', 'on');
set(gca, 'YMinorGrid', 'on');
grid on;

%title('STnet');

xlabel('Traffic demand (Gbps / node pair)');
ylabel('Average latency (ms)');

% Use the line handles so the legend shows the right markers
lg=legend([h1 h3 h2 h4], ...
  {'Multi-hop Bypass: single Q', ...
   'Hybrid Bypass: Q_{LP}', ...
   'Direct Bypass: single Q', ...
   'Hybrid Bypass: Q_{HP}'}, ...
  'Location', 'northeast');

set(lg, 'FontSize', 10);
set(1, 'position', [200, 200, 1000, 750]);
drawnow;
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2\Pareto\Fig9b.png', '-dpng', '-r300'); % 300 DPI
