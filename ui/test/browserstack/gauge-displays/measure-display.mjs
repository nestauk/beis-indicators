export default async ({log, driver, target, until, By, fail}) => {
	log('Navigating...');
	await driver.get(target);
	log("Searching for element...");
	await driver.wait(
		until.elementLocated(By.id('info')),
		20,
		'Element not found.',
		10
	);
	const info = await driver.findElement(By.id('info'));
	if (!info) {
		log('Element not found.');
		fail('Element not found.');
		return {
			error: 'Element not found',
		};
	}

	log('Found element. Getting text content...');
	const result = JSON.parse(await info.getText());
	log('Content:', result);
	return result;
}
