figureName = 'refreshFig.8_5a-energy-improve-Multihop-vs-Direct';   % <- change per figure
graphics_toolkit('qt');

% ---- Set figure appearance ----
set(gcf, 'Color', 'w');                     % white background
%set(gca, 'FontSize', 14, 'LineWidth', 1.0);
box on;
grid on;

## ComparePower6nodes_labels_final.m
close all; clf;
%figure(1, 'position',[100,100,720,540]);

x = [1, 2, 3, 4, 5, 6];  % x-axis data points

relOurMtoD6n = [20, 12.655; 40, 8.242;60, 6.641; 80, 5.425; 100, 4.100; 120, 4.076]
relOurMtoD14n = [20, 15.847; 40, 10.635; 60, 7.618;  80, 6.216; 100, 4.941; 120, 4.696]
relOurMtoD24n = [20, 15.725; 40, 10.715; 60, 8.340; 80, 6.278; 100, 5.623; 120, 4.739]




relOurMtoD6nY = relOurMtoD6n(:,2)
relOurMtoD14nY = relOurMtoD14n(:,2)
relOurMtoD24nY = relOurMtoD24n(:,2)

labels = {'20','40','60','80','100','120'};

plot( x, relOurMtoD24nY, 'k:d', x, relOurMtoD14nY, 'k--s', x, relOurMtoD6nY, 'k-o');

xlim([1, 6]);

ylim([3.5 16.5])
% Set the y-axis with minor gridlines
set(gca, 'YMinorTick', 'on'); % Turn on minor ticks
set(gca, 'YGrid', 'on');      % Enable grid for the y-axis
set(gca, 'YMinorGrid', 'on'); % Enable minor gridlines
grid on;

xticklabels(labels);

xlabel('Traffic demand (Gbps / node pair)');

ylabel('Power improvement (%)');

#title('Improvement of power consumption of Multi-hop Bypass relative to Direct Bypass based on simulation results');

legend('USnet', 'NSFnet', 'STnet', 'Location', 'northeast');

% High-resolution TIFF (Elsevier standard for print)
print([figureName '.png'], '-dpng', '-r600');
fprintf('Done! Exported %s.png at 600 DPI.\n', figureName);
