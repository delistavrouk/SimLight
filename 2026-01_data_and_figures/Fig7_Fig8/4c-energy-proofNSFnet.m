% ComparePower24nodes.m

dDeli = [20, 969.218; 40, 1583.190; 60, 2202.723; 80, 2820.248; 100, 3439.008; 120, 4054.384]
dST = [20, 920.000; 40, 1480.000; 60, 2130.000; 80, 2740.000; 100, 3350.000; 120, 4010.000]
mDeli = [20, 816.805; 40, 1413.547; 60, 2019.022; 80, 2643.180; 100, 3245.627; 120, 3862.240]
mST = [20, 750.000; 40, 1410.000; 60, 2040.000; 80, 2670.000; 100, 3280.000; 120, 3960.000]

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
ylim([600, 4200])

xticks([1 2 3 4 5 6]);

xticklabels(labels);

set(gca, 'YMinorTick', 'on'); % Turn on minor ticks
set(gca, 'YGrid', 'on');      % Enable grid for the y-axis
set(gca, 'YMinorGrid', 'on'); % Enable minor gridlines
grid on;

xlabel('Traffic demand (Gbps / node pair)');

ylabel('Average power consumption (kWatt)');

#title('Compare power consumption NSFnet N14L21');

%legend('Direct Bypass [our simulator]', 'Direct Bypass [Shen & Tucker]', 'Multi-hop Bypass [our simulator]', 'Multi-hop Bypass [Shen & Tucker]', 'Location', 'northwest');

