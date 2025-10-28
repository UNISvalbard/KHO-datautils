function spectralimage=read_miss_spectral(filename)
%
% Reads a MISS-image and corrects the "smiley" spectral image into
% a nice rectangular image.
%
% Outputs a matrix with the vertical axis being a proxy for the scan
% angle (no calibration yet). The horizontal axis is wavelength from
% 400nm to 700nm
% 
% Example:
%
% >> filename=fullfile('Data','MISS-20221221-090500.pgm');
% >> i=read_miss_spectral(filename);
% >> imagesc(400:700,1:200,i)
% >> xlabel('Wavelength [nm]')
%
%

% From quick calibration efforts using auroral emission lines,
% see plot_misspeaks.m

bluepoly=[-0.000401186790506   0.118021155830754  86.670020639834831];
redpoly=100*[-0.000003147574819   0.001045665634675   6.566050051599582];
greenpoly=100*[-0.000003805469556   0.001139447884417   4.625405056759545];


im=double(imread(filename)); % im2double would scale the intensity to 0..1
im=transpose(medfilt2(im));

% Estimate the background level from the image corner
% and remove the offset
bg_estimate=im(1:30,1:30);
bg_level=mean(bg_estimate(:));
im=max(0,im-bg_level);

% Create a spectral image
% - use data between rows 70 and 270 (needs scan angle calibration!)
% - interpolate data from 400..700nm
scanangle=1:200;
wavelengths=400:700;
spectralimage=zeros(length(scanangle),length(wavelengths));

for alpha=scanangle
    row=70+alpha;
    blueline=polyval(bluepoly,row); % Locations of the blue and red
    redline=polyval(redpoly,row);   % lines at this scan angle
    greenline=polyval(greenpoly,row);
    lambdas=polyfit([427.8, 557.7, 630.0],[blueline,greenline, redline],2);

    cols=polyval(lambdas,wavelengths);
    thisrowvalues=im(row,:);
    spectralvalues=interp1(thisrowvalues,cols,'linear');
    spectralimage(alpha,:)=spectralvalues;
end
end
