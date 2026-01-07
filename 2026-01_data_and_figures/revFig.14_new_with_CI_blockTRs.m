## ComparePower6nodes_octave_fixed_with_errorbars_3curves.m
## -------------------------------------------------------------------------
## Plot latency (left y-axis) and blocking rate (right y-axis)
## for 3 traffic splits, each with confidence intervals (T error bars).
## Works in pure GNU Octave (no yyaxis).
## -------------------------------------------------------------------------

close all; clf;

## --- Local helper function ----------------------------------------------
## Draw T-shaped vertical error bars with the same color as the main curve.
## Returns handle to the main line (for legend use).
##
## Usage:
##   h = terrorbar(x, y, ci, style, cap, color)
##
function h = terrorbar(x, y, ci, style, cap, color)
  if nargin < 6, color = 'k'; end
  %h = plot(x, y, style, 'LineWidth', 1.2, 'MarkerSize', 6, 'MarkerFaceColor', 'w', 'Color', color);
  h = plot(x, y, style, 'MarkerSize', 6, 'MarkerFaceColor', 'w', 'Color', color);
  for i = 1:numel(x)
    % vertical bar
    %line([x(i) x(i)], [y(i)-ci(i), y(i)+ci(i)], 'Color', color, 'LineWidth', 1);
    line([x(i) x(i)], [y(i)-ci(i), y(i)+ci(i)], 'Color', color);
    % horizontal caps
    %line([x(i)-cap x(i)+cap], [y(i)+ci(i) y(i)+ci(i)], 'Color', color, 'LineWidth', 1);
    %line([x(i)-cap x(i)+cap], [y(i)-ci(i) y(i)-ci(i)], 'Color', color, 'LineWidth', 1);
    line([x(i)-cap x(i)+cap], [y(i)+ci(i) y(i)+ci(i)], 'Color', color);
    line([x(i)-cap x(i)+cap], [y(i)-ci(i) y(i)-ci(i)], 'Color', color);
  end
endfunction

## --- Data ---------------------------------------------------------------
Lat10_90split = [5.196 5.363 5.401];
Lat30_70split = [5.079 5.442 5.559];
Lat50_50split = [4.94 5.357 5.73];

%BlckLPperc10_90split = [57.4 39.3 22];
%BlckLPperc30_70split = [56.9 38.5 20.9];
%BlckLPperc50_50split = [56.7 38 19.8];

BlckTRperc10_90split = [42.072 31.501 19.182];
BlckTRperc30_70split = [56.848 37.832 19.303];
BlckTRperc50_50split = [64.814 44.12 20.16];

ciLat10_90split = [0.023 0.02 0.014];
ciLat30_70split = [0.024 0.024 0.017];
ciLat50_50split = [0.026 0.022 0.026];

%ciBlckLPperc10_90split = [0.322 0.357 0.347];
%ciBlckLPperc30_70split = [0.334 0.34 0.309];
%ciBlckLPperc50_50split = [0.302 0.37 0.336];

ciBlckTRperc10_90split = [0.237773094333322 0.294340647381854 0.297283329475621];
ciBlckTRperc30_70split = [0.338810638316794 0.380271700060686 0.274455525403058];
ciBlckTRperc50_50split = [0.31436566356135 0.396030833324874 0.328131384205189];

x = 1:3;
labels = {"100", "200", "400"};

## --- Axis 1: Bars (right y-axis) ----------------------------------------
axBars = axes();
hold(axBars, "on");

barWidth = 0.25;
x1 = x - barWidth;    # Q_HP 10%
x2 = x;               # Q_HP 30%
x3 = x + barWidth;    # Q_HP 50%

bh1 = bar(axBars, x1, BlckTRperc10_90split, barWidth, "FaceColor", "#666666", "EdgeColor", "k");
bh2 = bar(axBars, x2, BlckTRperc30_70split, barWidth, "FaceColor", "#999999", "EdgeColor", "k");
bh3 = bar(axBars, x3, BlckTRperc50_50split, barWidth, "FaceColor", "#cccccc", "EdgeColor", "k");

## Add T error bars for blocking rates
capw = 0.08;
for i = 1:numel(x)
  % Red-ish (10/90)
  line([x1(i) x1(i)], [BlckTRperc10_90split(i)-ciBlckTRperc10_90split(i), ...
                        BlckTRperc10_90split(i)+ciBlckTRperc10_90split(i)], ...
       "Color", "k"); %, "LineWidth", 1);
  line([x1(i)-capw x1(i)+capw], [BlckTRperc10_90split(i)+ciBlckTRperc10_90split(i), ...
                                  BlckTRperc10_90split(i)+ciBlckTRperc10_90split(i)], ...
       "Color", "k"); %, "LineWidth", 1);
  line([x1(i)-capw x1(i)+capw], [BlckTRperc10_90split(i)-ciBlckTRperc10_90split(i), ...
                                  BlckTRperc10_90split(i)-ciBlckTRperc10_90split(i)], ...
       "Color", "k"); %, "LineWidth", 1);

  % Green (30/70)
  line([x2(i) x2(i)], [BlckTRperc30_70split(i)-ciBlckTRperc30_70split(i), ...
                        BlckTRperc30_70split(i)+ciBlckTRperc30_70split(i)], ...
       "Color", "k"); %, "LineWidth", 1);
  line([x2(i)-capw x2(i)+capw], [BlckTRperc30_70split(i)+ciBlckTRperc30_70split(i), ...
                                  BlckTRperc30_70split(i)+ciBlckTRperc30_70split(i)], ...
       "Color", "k"); %, "LineWidth", 1);
  line([x2(i)-capw x2(i)+capw], [BlckTRperc30_70split(i)-ciBlckTRperc30_70split(i), ...
                                  BlckTRperc30_70split(i)-ciBlckTRperc30_70split(i)], ...
       "Color", "k"); %, "LineWidth", 1);

  % Blue (50/50)
  line([x3(i) x3(i)], [BlckTRperc50_50split(i)-ciBlckTRperc50_50split(i), ...
                        BlckTRperc50_50split(i)+ciBlckTRperc50_50split(i)], ...
       "Color", "k"); %, "LineWidth", 1);
  line([x3(i)-capw x3(i)+capw], [BlckTRperc50_50split(i)+ciBlckTRperc50_50split(i), ...
                                  BlckTRperc50_50split(i)+ciBlckTRperc50_50split(i)], ...
       "Color", "k"); %, "LineWidth", 1);
  line([x3(i)-capw x3(i)+capw], [BlckTRperc50_50split(i)-ciBlckTRperc50_50split(i), ...
                                  BlckTRperc50_50split(i)-ciBlckTRperc50_50split(i)], ...
       "Color", "k"); %, "LineWidth", 1);
endfor

set(axBars, "XTick", x, "XTickLabel", labels);
set(axBars, "YAxisLocation", "right");
ylim(axBars, [0 100]);
ylabel(axBars, "Traffic demands blocking rate (%)");
xlabel(axBars, "λ capacity (Gbps)");
grid(axBars, "on");

## --- Axis 2: Lines (left y-axis, transparent foreground) ----------------
pos = get(axBars, "Position");
axLines = axes("Position", pos, "Color", "none");
hold(axLines, "on");

## Plot 3 curves with T error bars
ph1 = terrorbar(x, Lat10_90split, ciLat10_90split, "r-o", 0.05, "k");
ph2 = terrorbar(x, Lat30_70split, ciLat30_70split, "g--s", 0.05, "k");
ph3 = terrorbar(x, Lat50_50split, ciLat50_50split, "b:d", 0.05, "k");

set(axLines, "XTick", x, "XTickLabel", labels);
xlim(axLines, [0.5 3.5]);
ylim(axLines, [4.9 5.8]);
ylabel(axLines, "Latency mean Q_{HP}, Q_{LP} (ms)");
grid(axLines, "on");
set(axLines, "YMinorTick", "on");
set(axLines, "YMinorGrid", "on");

## --- Title & Legend -----------------------------------------------------
%title(axLines, "Hybrid Bypass, NSFnet, 1 fiber/link, 40 λ/fiber, Traffic load 400G, No λ converters, Varying traffic splits");

hleg = legend(axLines, [ph1 ph2 ph3 bh1 bh2 bh3], ...
  {"Q_{HP} 10%, Q_{LP} 90% (Latency)", ...
   "Q_{HP} 30%, Q_{LP} 70% (Latency)", ...
   "Q_{HP} 50%, Q_{LP} 50% (Latency)", ...
   "Q_{HP} 10%, Q_{LP} 90% (Blocking)", ...
   "Q_{HP} 30%, Q_{LP} 70% (Blocking)", ...
   "Q_{HP} 50%, Q_{LP} 50% (Blocking)"}, ...
   "location", "northwest");

pos = get(hleg, "position");
pos(2) = pos(2) - 0.05;
set(hleg, "position", pos);

## Keep axes perfectly synced
set(axLines, "Position", get(axBars, "Position"));
linkaxes([axBars axLines], "x");


set(hleg, 'FontSize', 10);
%set(1, 'position', [200, 200, 1000, 750]);
drawnow;
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2graphsGNUoctave\Fig14.png', '-dpng', '-r300'); % 300 DPI
