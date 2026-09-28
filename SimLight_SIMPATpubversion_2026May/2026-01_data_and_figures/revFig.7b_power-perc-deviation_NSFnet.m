%figureName = 'new_Fig.7_power-perc-deviation_NSFnet';   % <- change per figure
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
dDeliY =    [315.788;515.367;711.65;915.18;1113.029;1322.948];
dSTY   =    [303.0;497.0;687.0;877.0;1093.0;1295.0];
mDeliY =    [265.745;460.558;657.44;858.295;1058.031;1260.818];
mSTY   =    [260.0;458.0;670.0;859.0;1084.0;1282.0];

dDeliDevY = [4.0;3.6;3.5;4.2;1.8;2.1];
mDeliDevY = [2.2;0.6;1.9;0.1;2.5;1.7];

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
ylim(ax1, [200 1400]);
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

%#title(ax1, "NSFnet");

lg = legend([ph1 ph2 ph3 ph4 hDevDirect hDevMultihop], ...
  {"Direct Bypass [our simulator]", ...
   "Direct Bypass [Shen & Tucker]", ...
   "Multi-hop Bypass [our simulator]", ...
   "Multi-hop Bypass [Shen & Tucker]", ...
   "Direct Bypass deviation (%)", ...
   "Multi-hop deviation (%)"}, ...
  "location", "northwest");

%hold(ax1, "off");

set(lg, 'FontSize', 10);
set(1, 'position', [200, 200, 1000, 750]);
drawnow;
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2graphsGNUoctave\Fig7b.png', '-dpng', '-r300'); % 300 DPI

