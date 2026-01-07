box on;
grid on;
close all; clf; clear; clc;

x = [1, 2, 3, 4, 5, 6];

labels = {'20','40','60','80','100','120'};

hold on;

LatSTnetDirect = [3.837;3.856;3.838;3.832;3.837;3.835];
ciLatSTnetDirect = [0;0.021;0.026;0.027;0.03;0.031];
LatSTnetMultihop = [4.867;4.563;4.353;4.254;4.147;4.144];
ciLatSTnetMultihop = [0.067;0.071;0.062;0.048;0.044;0.048];

%LatSTnetHybridBypassNoRevisits = [3.791;4.033;3.943;3.918;3.893;3.89];
%ciLatSTnetHybridBypassNoRevisits = [0;0.031;0.025;0.024;0.024;0.024];
%LatSTnetHybridBypassNoRevisitsQhp = [3.791;3.791;3.794;3.787;3.795;3.797];
%ciLatSTnetHybridBypassNoRevisitsQhp = [0;0;0.02;0.02;0.025;0.025];

LatSTnetHyByQHP = [3.791	3.791	3.79371	3.78701	3.79484	3.79683]
ciLatSTnetHyByQHP = [5.31365E-16	5.31365E-16	0.019834337	0.019585376	0.025072957	0.02491161]

LatSTnetHyByQLP = [3.791	4.27405	4.09346	4.04821	3.99119	3.98327]
ciLatSTnetHyByQLP = [5.31365E-16	0.061340544	0.044280974	0.041919073	0.042069131	0.039753084]

Direct1Q      = LatSTnetDirect
ciDirect1Q    = ciLatSTnetDirect
Multihop1Q    = LatSTnetMultihop
ciMultihop1Q  = ciLatSTnetMultihop
HyByQHP       = LatSTnetHyByQHP
ciHyByQHP     = ciLatSTnetHyByQHP
HyByQLP       = LatSTnetHyByQLP
ciHyByQLP     = ciLatSTnetHyByQLP

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
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2\Pareto\Fig9a.png', '-dpng', '-r300'); % 300 DPI
