%graphics_toolkit('qt');

% ---- Set figure appearance ----
%set(gcf, 'Color', 'w');                     % white background
%set(gca, 'FontSize', 14, 'LineWidth', 1.0);
box on;
grid on;

## ComparePower6nodes_labels_final.m
close all; clf; clear; clc;
%figure(1, 'position',[100,100,700,700]);

%close all; clear; clc;
%graphics_toolkit('gnuplot')
%graphics_toolkit('qt')
%graphics_toolkit('fltk')

%figure('position', [100, 100, 1200, 800])  % Larger figure = finer detail
%set(gca, 'FontSize', 14, 'LineWidth', 1.0)


% Data
STnet = [0.2211 0.1163 0.0943 0.0790 0.0612 0.0615];
NSFnet = [0.3242 0.1877 0.1617 0.1278 0.1210 0.0979];
USnet = [0.3740 0.2320 0.2051 0.1690 0.1484 0.1293];

% Convert to percentage
data = [STnet; NSFnet; USnet]';
data_pct = data * 100;

% Grayscale colors
colors = [0.2 0.2 0.2; 0.5 0.5 0.5; 0.8 0.8 0.8];  % dark to light gray

% Create grouped bar chart
h = bar(data_pct, 'grouped');

ylim([-1 40])
% Set the y-axis with minor gridlines
set(gca, 'YMinorTick', 'on'); % Turn on minor ticks
set(gca, 'YGrid', 'on');      % Enable grid for the y-axis
set(gca, 'YMinorGrid', 'on'); % Enable minor gridlines
grid on;

% Labels and title

lg=legend('STnet', 'NSFnet', 'USnet');

xlabel('Traffic demand (Gbps / node pair)');
ylabel('Latency improvement (%)');

% Apply grayscale colors
for i = 1:numel(h)
    set(h(i), 'FaceColor', colors(i, :));
end

% Get actual X positions for labeling
x = get(h(1), 'XData');

% Set custom X-axis labels
xticks(x);
xticklabels({'20', '40', '60', '80', '100', '120'});


%drawnow;
%pause(0.05);

% --- Trim borders and export ---
set(gca,'LooseInset',get(gca,'TightInset'));
set(gca, 'Position', [0.08 0.08 0.88 0.88]);

set(lg, 'FontSize', 10);
set(1, 'position', [200, 200, 1000, 750]);
drawnow;
print('U:\My Drive\DELISTAVROU_KONSTANTINOS\2025-07 Journal\_rev2graphsGNUoctave\Fig10.png', '-dpng', '-r300'); % 300 DPI



