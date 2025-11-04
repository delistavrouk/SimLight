graphics_toolkit('qt');

% ---- Set figure appearance ----
set(gcf, 'Color', 'w');                     % white background
set(gca, 'FontSize', 14, 'LineWidth', 1.0);
box on;
grid on;

## ComparePower6nodes_labels_final.m
close all; clf; clear; clc;
figure(1, 'position',[100,100,700,700]);

%close all; clear; clc;
%graphics_toolkit('gnuplot')
%graphics_toolkit('qt')
%graphics_toolkit('fltk')

%figure('position', [100, 100, 1200, 800])  % Larger figure = finer detail
set(gca, 'FontSize', 14, 'LineWidth', 1.0)


% Data
% positive means that the Direct is better, negative means that the Hybrid is better
STnet  = [0.027540324 0.005828307 -0.017099364 0.015330958 0.007661705 0.000805351]; %Hybrid vs Direct
%STnet  = [-0.026802183 -0.005794535 0.017396839 -0.015099468 -0.007603449 -0.000804703]; %Direct vs Hybrid
NSFnet = [0.018778421 0.002681757 -0.001701158 0.001303438 -0.00066832 -0.001674677];
%NSFnet = [-0.018432292 -0.002674584 0.001704057 -0.001301741 0.000668767 0.001677486];
USnet  = [0.015709572 0.001313816 -0.011861273 -0.000368191 -0.004436768 -0.000314033];
%USnet  = [-0.015466598 -0.001312092 0.012003652 0.000368327 0.004456541 0.000314132];

% Convert to percentage
data = [STnet; NSFnet; USnet]';
data_pct = data * 100;

% Grayscale colors
colors = [0.2 0.2 0.2; 0.5 0.5 0.5; 0.8 0.8 0.8];  % dark to light gray

% Create grouped bar chart
h = bar(data_pct, 'grouped');


#ylim([-6 39])
% Set the y-axis with minor gridlines
set(gca, 'YMinorTick', 'on'); % Turn on minor ticks
set(gca, 'YGrid', 'on');      % Enable grid for the y-axis
set(gca, 'YMinorGrid', 'on'); % Enable minor gridlines
grid on;


% Labels and title

legend('STnet', 'NSFnet', 'USnet');

xlabel('Traffic demand (Gbps / node pair)');
ylabel('Power consumption difference (%)');

% Apply grayscale colors
for i = 1:numel(h)
    set(h(i), 'FaceColor', colors(i, :));
end

% Get actual X positions for labeling
x = get(h(1), 'XData');

% Set custom X-axis labels
xticks(x);
xticklabels({'20', '40', '60', '80', '100', '120'});



drawnow;
pause(0.05);

% --- Trim borders and export ---
set(gca,'LooseInset',get(gca,'TightInset'));
set(gca, 'Position', [0.08 0.08 0.88 0.88]);
% High-resolution TIFF (Elsevier standard for print)
%figure(1, 'position',[100,100,600,600]);
figureName = 'updFig12_9relativePowerImprovemHybridvsDirect';   % <- change per figure
print([figureName '.png'], '-dpng', '-r600');
fprintf('Done! Exported %s.png at 600 DPI.\n', figureName);







