package util.tests;

import junit.framework.Assert;

import org.junit.Test;

import util.ds.ZModuloNZRing;

public class ZModuloNZRingTests {

	@Test
	public void testOrd() {
		ZModuloNZRing f11 = new ZModuloNZRing(11);
		Assert.assertEquals(1, f11.getRestklassen().get(1).ord());
		Assert.assertEquals(10, f11.getRestklassen().get(2).ord());
		Assert.assertEquals(5, f11.getRestklassen().get(3).ord());
		Assert.assertEquals(5, f11.getRestklassen().get(4).ord());
		Assert.assertEquals(5, f11.getRestklassen().get(5).ord());
		Assert.assertEquals(10, f11.getRestklassen().get(6).ord());
		Assert.assertEquals(10, f11.getRestklassen().get(7).ord());
		Assert.assertEquals(10, f11.getRestklassen().get(8).ord());
		Assert.assertEquals(5, f11.getRestklassen().get(9).ord());
		Assert.assertEquals(2, f11.getRestklassen().get(10).ord());
	}

}
