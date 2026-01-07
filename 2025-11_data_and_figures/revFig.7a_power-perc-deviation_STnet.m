%figureName = 'new_Fig.7_power-perc-deviation_STnet';   % <- change per figure
%graphics_toolkit('qt');

% ---- Set figure appearance ----
set(gcf, 'Color', 'w');                     % white background
%set(gca, 'FontSize', 14, 'LineWidth', 0.6);
box on;
grid on;

%## ComparePower6nodes_labels_final.m
close all; clf;
%figure(1, 'position',[100,100,720,540]);

%## --- Data ---------------------------------------------------------------
dDeliY =    [51.706;83.863;115.59;146.676;178.204;210.157];
dSTY   =    [52.2;85.4;113.5;147;180.2;NaN];
mDeliY =    [45.162;76.951;107.914;138.719;170.898;201.591];
mSTY   =    [46;79.7;110.5;144.5;176;NaN];

dDeliDevY = [0.955401694;1.832605322;1.808114889;0.221052189;1.119797949;NaN];
mDeliDevY = [1.854572484;3.571999433;2.396770156;4.167725465;2.98521969;NaN];

x = 1:6;
labels = {"20","40","60","80","100","120"};

%## --- Plot power lines ----------------------------------------------------
ax1 = axes();
hold(ax1, "on");

%ph1 = plot(ax1, x, dDeliY, "k-o", "linewidth", 0.9, "markerfacecolor", "k");
%ph2 = plot(ax1, x, dSTY,   "k--s", "linewidth", 0.9, "markerfacecolor", "w");
%ph3 = plot(ax1, x, mDeliY, "k:d",  "linewidth", 0.9, "markerfacecolor", "k");
%ph4 = plot(ax1, x, mSTY,   "k-.p", "linewidth", 0.9, "markerfacecolor", "w");

ph1 = plot(ax1, x, dDeliY, "k-o",  "markerfacecolor", "k");
ph2 = plot(ax1, x, dSTY,   "k--s", "markerfacecolor", "w");
ph3 = plot(ax1, x, mDeliY, "k:d",  "markerfacecolor", "k");
ph4 = plot(ax1, x, mSTY,   "k-.p", "markerfacecolor", "w");

xlim(ax1, [0.5 6.5]);
ylim(ax1, [25 220]);
set(ax1, "xtick", x, "xticklabel", labels);
xlabel(ax1, "Traffic demand (Gbps / node pair)");
ylabel(ax1, "Average power consumption (kW)");
grid(ax1, "on");
set(ax1, "yminortick", "on", "yminorgrid", "on");

%## --- Deviation labels ----------------------------------------------------
offset_up   =  8;    % upward offset for Direct (gray)
offset_down = 10;    % downward offset for Multi-hop (blue)
shift_gray  = -0.12; % leftward shift for Direct deviation
shift_blue  =  0.15; % rightward shift for Multi-hop deviation
%set(legend(ax1), 'FontSize', 10);

for i = 1:numel(x)
  if ~isnan(dDeliDevY(i))
    text(x(i)+shift_gray, dDeliY(i) + offset_up, ...
         sprintf("%.1f%%", dDeliDevY(i)), ...
         "color", [0.40 0.40 0.40], "fontsize", 10, ...
         "fontangle", "italic", ...
         "horizontalalignment", "right", ...
         "verticalalignment", "bottom");
  end
  if ~isnan(mDeliDevY(i))
    text(x(i)+shift_blue, mDeliY(i) - offset_down, ...
         sprintf("%.1f%%", mDeliDevY(i)), ...
         "color", [0.00 0.00 0.60], "fontsize", 10, ...
         "fontangle", "italic", ...
         "horizontalalignment", "left", ...
         "verticalalignment", "top");
  end
end

%## --- Legend --------------------------------------------------------------
hDevDirect   = plot(ax1, nan, nan, "-", "color", [0.40 0.40 0.40]);
hDevMultihop = plot(ax1, nan, nan, "-", "color", [0.00 0.00 0.60]);

%#title(ax1, "STnet");

lg = legend([ph1 ph2 ph3 ph4 hDevDirect hDevMultihop], ...
  {"Direct Bypass [our simulator]", ...
   "Direct Bypass [Shen & Tucker]", ...
   "Multi-hop Bypass [our simulator]", ...
   "Multi-hop Bypass [Shen & Tucker]", ...
   "Direct Bypass deviation (%)", ...
   "Multi-hop deviation (%)"}, ...
  "location", "northwest");

%hold(ax1, "off");

%lg = legend('USnet', 'NSFnet', 'STnet', 'Location', 'northeast');
set(lg, 'FontSize', 10);
set(1, 'position', [200, 200, 1000, 750]);
drawnow;
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2graphsGNUoctave\Fig7a.png', '-dpng', '-r300'); % 300 DPI
