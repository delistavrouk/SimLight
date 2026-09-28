close all; clf;

function h = terrorbar(x, y, ci, style, cap, color)
  if nargin < 6, color = 'k'; end
  h = plot(x, y, style, 'LineWidth', 1.2, 'MarkerSize', 6, ...
           'MarkerFaceColor', 'w', 'Color', color);
  for i = 1:numel(x)
    % vertical bar
    line([x(i) x(i)], [y(i)-ci(i), y(i)+ci(i)], 'Color', color, 'LineWidth', 1);
    % caps
    line([x(i)-cap x(i)+cap], [y(i)+ci(i) y(i)+ci(i)], 'Color', color, 'LineWidth', 1);
    line([x(i)-cap x(i)+cap], [y(i)-ci(i) y(i)-ci(i)], 'Color', color, 'LineWidth', 1);
  end
endfunction

## --- Data ---------------------------------------------------------------
LatWithWavConv = [5.086 5.38 5.554];
BlckLPpercWithWavConv = [65.637 42.911 14.468];
LatNoWavConv = [4.943 5.326 5.549];
BlckLPpercNoWavConv = [64.642 42.397 14.329];

ciLatWithWavConv = [0.029 0.02 0.015];
ciBlckLPpercWithWavConv = [0.378539831411166 0.413489344263867 0.285623668846769];
ciLatNoWavConv = [0.026 0.018 0.016];
ciBlckLPpercNoWavConv = [0.374032510951154 0.432504818447427 0.278152264247316];

x = 1:3;
labels = {"1", "2", "4"};

axBars = axes();
hold(axBars, "on");

barWidth = 0.35;
x1 = x - barWidth/2;   # With converters
x2 = x + barWidth/2;   # No converters

bh1 = bar(axBars, x1, BlckLPpercWithWavConv, barWidth, ...
          "FaceColor", "#666666", "EdgeColor", "k");
bh2 = bar(axBars, x2, BlckLPpercNoWavConv, barWidth, ...
          "FaceColor", "#cccccc", "EdgeColor", "k");

for i = 1:numel(x)
  % With λ converters (gray)
  line([x1(i) x1(i)], [BlckLPpercWithWavConv(i)-ciBlckLPpercWithWavConv(i), ...
                        BlckLPpercWithWavConv(i)+ciBlckLPpercWithWavConv(i)], ...
       "Color", "k", "LineWidth", 1);
  line([x1(i)-0.1 x1(i)+0.1], [BlckLPpercWithWavConv(i)+ciBlckLPpercWithWavConv(i), ...
                                BlckLPpercWithWavConv(i)+ciBlckLPpercWithWavConv(i)], ...
       "Color", "k", "LineWidth", 1);
  line([x1(i)-0.1 x1(i)+0.1], [BlckLPpercWithWavConv(i)-ciBlckLPpercWithWavConv(i), ...
                                BlckLPpercWithWavConv(i)-ciBlckLPpercWithWavConv(i)], ...
       "Color", "k", "LineWidth", 1);
  % No λ converters (blueish)
  line([x2(i) x2(i)], [BlckLPpercNoWavConv(i)-ciBlckLPpercNoWavConv(i), ...
                        BlckLPpercNoWavConv(i)+ciBlckLPpercNoWavConv(i)], ...
       "Color", "k", "LineWidth", 1);
  line([x2(i)-0.1 x2(i)+0.1], [BlckLPpercNoWavConv(i)+ciBlckLPpercNoWavConv(i), ...
                                BlckLPpercNoWavConv(i)+ciBlckLPpercNoWavConv(i)], ...
       "Color", "k", "LineWidth", 1);
  line([x2(i)-0.1 x2(i)+0.1], [BlckLPpercNoWavConv(i)-ciBlckLPpercNoWavConv(i), ...
                                BlckLPpercNoWavConv(i)-ciBlckLPpercNoWavConv(i)], ...
       "Color", "k", "LineWidth", 1);
endfor

set(axBars, "XTick", x, "XTickLabel", labels);
set(axBars, "YAxisLocation", "right");
ylim(axBars, [0 100]);
ylabel(axBars, "Traffic demands blocking rate (%)");
xlabel(axBars, "Number of fibers / link");
grid(axBars, "on");

pos = get(axBars, "Position");
axLines = axes("Position", pos, "Color", "none");
hold(axLines, "on");

## Plot lines with T error bars (and get handles for legend)
ph1 = terrorbar(x, LatWithWavConv, ciLatWithWavConv, "k-o", 0.05, "k");
ph2 = terrorbar(x, LatNoWavConv, ciLatNoWavConv, "k--s", 0.05, "k");

set(axLines, "XTick", x, "XTickLabel", labels);
xlim(axLines, [0.5 3.5]);
ylim(axLines, [4.8 5.7]);
ylabel(axLines, "Latency mean Q_{HP}, Q_{LP} (ms)");
grid(axLines, "on");
set(axLines, "YMinorTick", "on");
set(axLines, "YMinorGrid", "on");

%title(axLines, "Hybrid Bypass, NSFnet, λ capct 100Gbps, 40 λ/fiber, Traff. load 400G, Q_{HP}:50%, Q_{LP}:50%");

hleg = legend(axLines, [ph1 ph2 bh1 bh2], ...
  {"With λ converters (Latency)", ...
   "No λ converters (Latency)", ...
   "With λ converters (Blocking)", ...
   "No λ converters (Blocking)"}, ...
  "location", "northwest");

pos = get(hleg, "position");
pos(2) = pos(2) - 0.05;
set(hleg, "position", pos);

## Keep axes perfectly synced
set(axLines, "Position", get(axBars, "Position"));
linkaxes([axBars axLines], "x");

drawnow;

figureName = 'newFig12a_new_with_CI_blockTRs';   % <- change per figure
print([figureName '.png'], '-dpng', '-r600');
fprintf('Done! Exported %s.png at 600 DPI.\n', figureName);
