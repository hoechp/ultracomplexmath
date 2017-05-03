package util.tests;

import junit.framework.Assert;
import org.junit.Test;

import util.tinker.PolynominalGuess;

public class GuesserTest {

	@Test
	public void testGuesser() {
		System.out.println(new PolynominalGuess(3,
				2.53, 3.04, 3.70, 4.45, 5.31, 6.12, 6.90
				));
	}

}
