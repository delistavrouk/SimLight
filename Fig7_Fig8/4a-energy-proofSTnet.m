## ComparePower6nodes_octave.m  (Octave-only, no yyaxis/uistack)

close all; clf;

## --- Data ---------------------------------------------------------------
dDeliY =    [51.706;83.863;115.590;146.676;178.204;210.157];
dSTY   =    [52.200;85.400;113.500;147.000;180.200;NaN];
mDeliY =    [45.162;76.951;107.914;138.719;170.898;201.591];
mSTY   =    [46.000;79.700;110.500;144.500;176.000;NaN];

dDeliDevY = [01.550;05.670;005.910;007.360;006.530;NaN];
mDeliDevY = [03.180;06.740;006.850;007.200;007.850;NaN];

x = 1:6;
labels = {"20","40","60","80","100","120"};

## --- Axis 1 (bottom): BARS, right y-axis (background) -------------------
axBars = axes();  % create first, so it stays at the back
hold(axBars, "on");

% Two light bar series side-by-side
bh1 = bar(axBars, x-0.15, dDeliDevY, 0.3, "FaceColor", [0.85 0.85 0.85], "EdgeColor", "none");
bh2 = bar(axBars, x+0.15, mDeliDevY, 0.3, "FaceColor", [0.70 0.80 1.00], "EdgeColor", "none");

xlim(axBars, [0.5 6.5]);
ylim(axBars, [0 8]);
set(axBars, "XTick", x, "XTickLabel", labels);
set(axBars, "YAxisLocation", "right");   % right y-axis
ylabel(axBars, "Deviation (%)");
xlabel(axBars, "Traffic demand (Gbps / node pair)");

grid(axBars, "on");  % grid from bars axis (optional)

## --- Axis 2 (top): LINES, left y-axis (foreground, transparent) ---------
pos = get(axBars, "Position");
axLines = axes("Position", pos, "Color", "none");  % transparent background
hold(axLines, "on");

ph1 = plot(axLines, x, dDeliY, "k-o", "LineWidth", 1.2, "MarkerFaceColor", "k");
ph2 = plot(axLines, x, dSTY,   "k--s", "LineWidth", 1.2, "MarkerFaceColor", "w");
ph3 = plot(axLines, x, mDeliY, "k:d", "LineWidth", 1.2, "MarkerFaceColor", "k");
ph4 = plot(axLines, x, mSTY,   "k-.p", "LineWidth", 1.2, "MarkerFaceColor", "w");

xlim(axLines, [0.5 6.5]);
ylim(axLines, [30 220]);
set(axLines, "XTick", x, "XTickLabel", labels);  % keep ticks aligned

ylabel(axLines, "Average power consumption (kWatt)");
% Do NOT set xlabel on the top axis (keeps one x-label from axBars)

grid(axLines, "on");
set(axLines, "YMinorTick", "on");
set(axLines, "YMinorGrid", "on");

## --- Title & Legend (attach to top axis so it sits above) ---------------
title(axLines, "Power vs. Deviation");

% Build a combined legend using handles from both axes, displayed on top axis
legend(axLines, [ph1 ph2 ph3 ph4 bh1 bh2], ...
  {"Direct Bypass [our simulator]", ...
   "Direct Bypass [Shen & Tucker]", ...
   "Multi-hop Bypass [our simulator]", ...
   "Multi-hop Bypass [Shen & Tucker]", ...
   "Direct Bypass deviation", ...
   "Multi-hop Bypass deviation"}, ...
  "Location", "southeast");

## --- Keep axes perfectly synced on resize --------------------------------
% (Octave usually keeps same 'Position', but if you tweak, reapply:)
set(axLines, "Position", get(axBars, "Position"));

