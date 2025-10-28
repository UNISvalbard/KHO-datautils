%filename=fullfile('Data','MISS-20221221-120500.pgm')
filename=fullfile('.','MISS-20221225-162100.pgm');

im=double(imread(filename));
im=transpose(medfilt2(im));
%im=im(:,1:400);

% Estimate the background level from the image corner
% and remove the offset
bg_estimate=im(1:30,1:30);
bg_level=mean(bg_estimate(:));
im=max(0,im-bg_level);

clf
%subplot(3,1,1)
imagesc(sqrt(im))
caxis([0 50])

n=10;
bluepeaks=[];
greenpeaks=[];
redpeaks=[];

rows=90:10:250;
for row=rows
    slice=im(row+(-n:n),:);
    s=mean(slice,1);
    [~,loc]=findpeaks(s,'MinPeakDistance',30,'MinPeakHeight',30,'NPeaks',3);
    bluepeaks=[bluepeaks, loc(1)];
    greenpeaks=[greenpeaks, loc(2)];
    redpeaks=[redpeaks, loc(3)];
end

% Fit polynomials

[bluepoly,blueS]=polyfit(rows,bluepeaks,2);
[greenpoly,greenS]=polyfit(rows,greenpeaks,2);
[redpoly,redS]=polyfit(rows,redpeaks,2);

% Mark the spectral lines in the image
hold on
rownumber=1:size(im,1);
%plot(polyval(bluepoly,rownumber)-5,rownumber,'w')
%plot(polyval(bluepoly,rownumber)+5,rownumber,'w')
[x,delta]=polyval(bluepoly,rownumber,blueS);
plot(x,rownumber,'r')
plot(x-2*delta,rownumber,'w')
plot(x+2*delta,rownumber,'w')


[x,delta]=polyval(greenpoly,rownumber,greenS);
plot(x,rownumber,'r')
plot(x-2*delta,rownumber,'w')
plot(x+2*delta,rownumber,'w')

[x,delta]=polyval(redpoly,rownumber,redS);
plot(x,rownumber,'r')
plot(x-2*delta,rownumber,'w')
plot(x+2*delta,rownumber,'w')

% Check the linearity for each scan angle (latitude) by
% estimating the location of green peak based on blue and red
% peaks...

testline=zeros(size(rownumber));
greendiff=zeros(size(rownumber));
for i=rownumber
    blueline=polyval(bluepoly,i); % Locations of the blue and red
    redline=polyval(redpoly,i);   % lines at this scan angle
    greenline=polyval(greenpoly,i);
    lambdas=polyfit([427.8, 557.7, 630.0],[blueline,greenline, redline],2);
    testline(i)=polyval(lambdas,557);
    greendiff(i)=greenline-testline(i);
end

plot(testline,rownumber,'g')
hold off
