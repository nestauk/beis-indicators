import path from 'path';

export const isNotNuts3File = name => !path.parse(name).name.endsWith('.nuts3');
export const isNotLepFile = name => !path.parse(name).name.endsWith('.lep');
