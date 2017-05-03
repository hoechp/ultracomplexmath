package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.hypercomplex.Complex;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.HypercomplexLSE;

public class HypercomplexLSETest {
	
	@Test
	public void testHypercomplexLSE() {
		Hypercomplex c1 = new Complex(2, 1);
		Hypercomplex c2 = new Complex(0, 0);
		Hypercomplex l1 = new Complex(10, 0);
		Hypercomplex l2 = new Complex(10, 10);
		HypercomplexLSE lse_c = new HypercomplexLSE("complex", 2,
				c1,				c2,						l1,
				c2, 			c1,						l2,
				c2,				c2,						c2,
				c2,				c2,						c2,
				c1.plus(c2),	c1.plus(c2),			l1.plus(l2),
				c1.plus(c2),	c1.plus(c2),			l1.plus(l2));
		HypercomplexLSE lse_b = new HypercomplexLSE("binary", 2,
				c1,				c2,						l1,
				c2, 			c1,						l2,
				c2,				c2,						c2,
				c2,				c2,						c2,
				c1.plus(c2),	c1.plus(c2),			l1.plus(l2),
				c1.plus(c2),	c1.plus(c2),			l1.plus(l2));
		HypercomplexLSE lse_d = new HypercomplexLSE("dual", 2,
				c1,				c2,						l1,
				c2, 			c1,						l2,
				c2,				c2,						c2,
				c2,				c2,						c2,
				c1.plus(c2),	c1.plus(c2),			l1.plus(l2),
				c1.plus(c2),	c1.plus(c2),			l1.plus(l2));
		lse_c.solve();
		lse_b.solve();
		lse_d.solve();
		Assert.assertTrue(lse_c.getNumEquations() == lse_c.getNumVariables());
		Assert.assertTrue(lse_b.getNumEquations() == lse_b.getNumVariables());
		Assert.assertTrue(lse_d.getNumEquations() == lse_d.getNumVariables());
		Assert.assertTrue(lse_c.isSolved());
		Assert.assertTrue(lse_b.isSolved());
		Assert.assertTrue(lse_d.isSolved());
		HypercomplexLSE lse = new HypercomplexLSE(5,
				1, -1, 1, -1, 1,	-3,
				0, 0, 0, 0, 1,		-3,
				1, 1, 1, 1, 1,		3,
				16, 8, 4, 2, 1, 	3,
				81, 27, 9, 3, 1,	9);
		lse.solve();
		System.out.println(lse);
	}

}
