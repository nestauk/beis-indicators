export const browsers = [
	'opera',
	'chrome',
	'ie',
	'firefox',
	'edge',
	'safari',
	'iphone',
	'ipad',
	'android'
];

export const devices = [
	'iPhone XS',
	'iPhone 12 Pro Max',
	'iPhone 12 Pro',
	'iPhone 12 Mini',
	'iPhone 12',
	'iPhone 11 Pro Max',
	'iPhone 11',
	'iPad Air 4',
	'iPad Pro 12.9 2020',
	'iPad 8th',
	'iPhone 11 Pro',
	'iPhone 8',
	'iPhone SE 2020',
	'iPad Pro 12.9 2018',
	'iPad Pro 11 2020',
	'iPad Mini 2019',
	'iPad Air 2019',
	'iPad 7th',
	'iPhone XS Max',
	'iPhone XR',
	'iPhone 8 Plus',
	'iPhone 7',
	'iPhone 6S',
	'iPad Pro 11 2018',
	'iPhone X',
	'iPhone 6S Plus',
	'iPhone 6',
	'iPhone SE',
	'iPad Pro 9.7 2016',
	'iPad Pro 12.9 2017',
	'iPad Mini 4',
	'iPad 6th',
	'iPad 5th',
	'iPhone 7 Plus',
	'Samsung Galaxy S20',
	'Google Pixel 5',
	'Google Pixel 4',
	'Samsung Galaxy S20 Plus',
	'Samsung Galaxy S20 Ultra',
	'Samsung Galaxy Note 20 Ultra',
	'Samsung Galaxy Note 20',
	'Samsung Galaxy A51',
	'Samsung Galaxy A11',
	'Google Pixel 4 XL',
	'Google Pixel 3',
	'OnePlus 8',
	'OnePlus 7T',
	'Vivo Y50',
	'Oppo Reno 3 Pro',
	'Samsung Galaxy Tab S7',
	'Samsung Galaxy S9 Plus',
	'Samsung Galaxy S8 Plus',
	'Samsung Galaxy S10e',
	'Samsung Galaxy S10 Plus',
	'Samsung Galaxy S10',
	'Samsung Galaxy Note 10 Plus',
	'Samsung Galaxy Note 10',
	'Samsung Galaxy A10',
	'Google Pixel 3a XL',
	'Google Pixel 3a',
	'Google Pixel 3 XL',
	'Google Pixel 2',
	'Motorola Moto G7 Play',
	'OnePlus 7',
	'OnePlus 6T',
	'Xiaomi Redmi Note 8',
	'Xiaomi Redmi Note 7',
	'Samsung Galaxy Tab S6',
	'Samsung Galaxy Tab S5e',
	'Samsung Galaxy Note 9',
	'Samsung Galaxy J7 Prime',
	'Samsung Galaxy Tab S4',
	'Samsung Galaxy S9',
	'Google Pixel',
	'Samsung Galaxy Note 8',
	'Samsung Galaxy A8',
	'Samsung Galaxy S8',
	'Samsung Galaxy Tab S3',
	'Samsung Galaxy S7',
	'Google Nexus 6',
	'Motorola Moto X 2nd Gen',
	'Samsung Galaxy S6',
	'Samsung Galaxy Note 4',
	'Google Nexus 5',
	'Samsung Galaxy Tab 4'
]

const windowsResolutions = [
	'1024x768',
	// '1280x800',
	// '1280x1024',
	// '1366x768',
	// '1440x900',
	// '1680x1050',
	// '1600x1200',
	// '1920x1200',
	// '1920x1080',
	// '2048x1536'
];
export const windowsResolutionsOlder = [/* '800x600', */...windowsResolutions];
const osxResolutions = [
	'1024x768',
	// '1280x960',
	// '1280x1024',
	// '1600x1200',
	// '1920x1080'
];

export const operatingSystems = {
	'Windows': {
		'XP': windowsResolutionsOlder,
		'7': windowsResolutionsOlder,
		'8': windowsResolutions,
		'8.1': windowsResolutions,
		'10': windowsResolutions
	},
	'OS X': {
		'Snow Leopard': osxResolutions,
		'Lion': osxResolutions,
		'Mountain Lion': osxResolutions,
		'Mavericks': osxResolutions,
		'Yosemite': osxResolutions,
		'El Capitan': osxResolutions,
		'Sierra': osxResolutions,
		'High Sierra': osxResolutions,
		'Mojave': osxResolutions,
		'Catalina': osxResolutions,
		'Big Sur': osxResolutions,
	}
};


/*
Earliest browser versions published in 2019.
Taken from https://en.wikipedia.org/wiki/Timeline_of_web_browsers#2010s
*/
export const minVersions = {
	"Chrome": "72.0",
	"Opera": "58.0",
	"Firefox": "65.0",
	"Safari": "13.0",
	"Edge": "44.0"
};
