figureName = 'refreshFig.8_5b-latency-deteriorate-Multihop-vs-Direct';   % <- change per figure
graphics_toolkit('qt');

% ---- Set figure appearance ----
set(gcf, 'Color', 'w');                     % white background
%set(gca, 'FontSize', 14, 'LineWidth', 1.0);
box on;
grid on;

## ComparePower6nodes_labels_final.m
close all; clf;
%figure(1, 'position',[100,100,720,540]);

% LatRelDeterMhp2DrcSingleQ3nets.m
% LatRelDeterMhp2DrcSingleQ3nets.png

relSingleQueueMultihop2Direct6n = [20, 26.841; 40, 18.335; 60, 13.428; 80, 11.014; 100, 8.088; 120, 8.062]
relSingleQueueMultihop2Direct14n = [20, 45.969; 40, 32.391; 60, 23.938; 80, 19.065; 100, 16.353; 120, 12.918]
relSingleQueueMultihop2Direct24n = [20, 56.855; 40, 40.865; 60, 30.590; 80, 24.222; 100, 19.412; 120, 16.783]

relSingleQueueMultihop2Direct6nY = relSingleQueueMultihop2Direct6n(:,2)
relSingleQueueMultihop2Direct14nY = relSingleQueueMultihop2Direct14n(:,2)
relSingleQueueMultihop2Direct24nY = relSingleQueueMultihop2Direct24n(:,2)

x = [1, 2, 3, 4, 5, 6];  % x-axis data points

labels = {'20','40','60','80','100','120'};

plot(x, relSingleQueueMultihop2Direct24nY, 'k:d', x, relSingleQueueMultihop2Direct14nY, 'k--s', x, relSingleQueueMultihop2Direct6nY, 'k-o');

xlim([1, 6]);

minA = min(relSingleQueueMultihop2Direct6nY)
minB = min(relSingleQueueMultihop2Direct14nY)
minC = min(relSingleQueueMultihop2Direct24nY)
a = min([minA, minB, minC])

maxA = max(relSingleQueueMultihop2Direct6nY)
maxB = max(relSingleQueueMultihop2Direct14nY)
maxC = max(relSingleQueueMultihop2Direct24nY)
b = max([maxA, maxB, maxC])

ylim([0 60])

xticks([1 2 3 4 5 6]);

xticklabels(labels);


% Set the y-axis with minor gridlines
set(gca, 'YMinorTick', 'on'); % Turn on minor ticks
set(gca, 'YGrid', 'on');      % Enable grid for the y-axis
set(gca, 'YMinorGrid', 'on'); % Enable minor gridlines
grid on;

xlabel('Traffic demand (Gbps / node pair)');

ylabel('Latency deterioration (%)');

#title('Latency deterioration of Single Q: Multi-hop Bypass relative to Single Q: Direct bypass (Sim, Single Q)');

legend('USnet', 'NSFnet', 'STnet', 'Location', 'northeast');

% High-resolution TIFF (Elsevier standard for print)
print([figureName '.png'], '-dpng', '-r600');
fprintf('Done! Exported %s.png at 600 DPI.\n', figureName);
