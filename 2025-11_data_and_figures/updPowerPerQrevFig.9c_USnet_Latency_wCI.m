box on;
grid on;
close all; clf; clear; clc;

x = [1, 2, 3, 4, 5, 6];

labels = {'20','40','60','80','100','120'};

%box on
%grid on
hold on;

LatUSnetDirect = [5.069;5.065;5.065;5.071;5.078;5.071];
ciLatUSnetDirect = [0;0.008;0.008;0.01;0.009;0.011];
LatUSnetMultihop = [7.952;7.135;6.614;6.299;6.063;5.922];
ciLatUSnetMultihop = [0.028;0.031;0.026;0.02;0.02;0.02];

%LatUSnetHybridBypassNoRevisits = [4.977;5.479;5.258;5.234;5.163;5.156];
%ciLatUSnetHybridBypassNoRevisits = [0;0.011;0.01;0.008;0.009;0.008];
%LatUSnetHybridBypassNoRevisitsQhp = [4.977;4.977;4.979;4.969;4.976;4.976];
%ciLatUSnetHybridBypassNoRevisitsQhp = [0;0;0.007;0.006;0.009;0.008];

LatUSnetHyByQHP = [4.977	4.977	4.97886	4.96908	4.97607	4.97589]
ciLatUSnetHyByQHP = [2.12546E-15	2.12546E-15	0.007327045	0.005684569	0.009103501	0.008263644]

LatUSnetHyByQLP = [4.977	5.98103	5.53665	5.49937	5.35023	5.33576]
ciLatUSnetHyByQLP = [2.12546E-15	0.02252842	0.018246502	0.015098331	0.01490983	0.012631608]

Direct1Q      = LatUSnetDirect
ciDirect1Q    = ciLatUSnetDirect
Multihop1Q    = LatUSnetMultihop
ciMultihop1Q  = ciLatUSnetMultihop
HyByQHP       = LatUSnetHyByQHP
ciHyByQHP     = ciLatUSnetHyByQHP
HyByQLP       = LatUSnetHyByQLP
ciHyByQLP     = ciLatUSnetHyByQLP

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
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2\Pareto\Fig9c.png', '-dpng', '-r300'); % 300 DPI

