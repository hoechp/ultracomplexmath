package util.tests;

import org.junit.Test;

import util.hypercomplex.ultracomplex.Ultra;

public class UltraBugTest {

	@Test
	public void testUltraBug() {
		double d = 0.2;
		Ultra a = new Ultra(d, d, d, d, 0, 0, 0, 0); // without dual TODO: check csc, cot, coth; fix that type of bug in GENERAL
		UltraTest.printTrig(a);
		a = new Ultra(d, 0, d, 0, d, 0, d, 0); // without binary
		UltraTest.printTrig(a);
		a = new Ultra(d, d, 0, 0, d, d, 0, 0); // without complex
		UltraTest.printTrig(a);
		a = new Ultra(d, d, d, d, d, d, d, d); // allx
		UltraTest.printTrig(a);
	}

}