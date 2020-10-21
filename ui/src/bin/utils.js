import path from 'path';

/* NUTS */
export const isNotNuts3File = name => !path.parse(name).name.endsWith('.nuts3');
export const isNuts3File = name => path.parse(name).name.endsWith('.nuts3');

/* LEP */
export const isNotLepFile = name => !path.parse(name).name.endsWith('.lep');
export const isLepFile = name => path.parse(name).name.endsWith('.lep');
