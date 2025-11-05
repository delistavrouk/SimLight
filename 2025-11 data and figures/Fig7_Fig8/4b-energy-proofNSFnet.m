% ComparePower14nodes.m

dDeli = [20, 315.788; 40, 515.367; 60, 711.650; 80, 915.180; 100, 1113.029; 120, 1322.948]
dST = [20, 303.000; 40, 497.000; 60, 687.000; 80, 877.000; 100, 1093.000; 120, 1295.000]
mDeli = [20, 265.745; 40, 460.558; 60, 657.440; 80, 858.295; 100, 1058.031; 120, 1260.818]
mST = [20, 260.000; 40, 458.000; 60, 670.000; 80, 859.000; 100, 1084.000; 120, 1282.000]

dDeliY = dDeli(:, 2)
dSTY = dST(:, 2)
mDeliY = mDeli(:, 2)
mSTY = mST(:, 2)

x = [1, 2, 3, 4, 5, 6];  % x-axis data points

labels = {"20","40","60","80","100","120"};

plot(x, dDeliY, 'k-o', x, dSTY, 'k--s', x, mDeliY, 'k:d', x, mSTY, 'k-.p' );

xlim([1, 6]);

minA = min(dDeliY)
minB = min(dSTY)
minC = min(mDeliY)
minD = min(mSTY)
a = min([minA, minB, minC, minD])

maxA = max(dDeliY)
maxB = max(dSTY)
maxC = max(mDeliY)
maxD = max(mSTY)
b = max([maxA, maxB, maxC, maxD])

#ylim([a-100, b+80])
ylim([200, 1400])

xticks([1 2 3 4 5 6]);

xticklabels(labels);

% Set the y-axis with minor gridlines
set(gca, 'YMinorTick', 'on'); % Turn on minor ticks
set(gca, 'YGrid', 'on');      % Enable grid for the y-axis
set(gca, 'YMinorGrid', 'on'); % Enable minor gridlines
grid on;

xlabel('Traffic demand (Gbps / node pair)');

ylabel('Average power consumption (kWatt)');

#title('Compare power consumption NSFnet N14L21');

%legend('Direct Bypass [our simulator]', 'Direct Bypass [Shen & Tucker]', 'Multi-hop Bypass [our simulator]', 'Multi-hop Bypass [Shen & Tucker]', 'Location', 'northwest');

