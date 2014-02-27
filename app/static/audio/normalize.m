files = dir('*.wav');
for ii = 1:numel(files)
    file = files(ii);
    disp(['Converting ' file.name]);
    [x,Fs] = wavread(file.name);
    x = x/max(abs(x))*.999;
    wavwrite(x, Fs, file.name);
end