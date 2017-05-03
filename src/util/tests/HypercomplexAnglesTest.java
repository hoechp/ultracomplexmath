package util.tests;

import java.util.Vector;

import junit.framework.Assert;

import org.junit.Test;

import util.basics.Vectors;
import util.hypercomplex.Hypercomplex;
import util.hypercomplex.Complex;
import util.hypercomplex.Dual;
import util.hypercomplex.Binary;

public class HypercomplexAnglesTest {
	
	@Test
	public void testHypercomplexAngles2() {
		double diff = 0.0001;
		for (int i = 0; i < Tests.MULTITEST_COUNT; ++i) {
			double imPhi = ((Math.random() - 0.5) * 2) * 4 * Math.PI;
			double phi = ((Math.random() - 0.5) * 2) * 4 * Math.PI;

			// binary
			Hypercomplex binary = new Binary(phi, imPhi);
			Vector<Double> binaryAngledVector = Vectors.vectorFromHypercomplexAngle(binary);
			Hypercomplex testBin = Hypercomplex.binary3DAngle(binaryAngledVector);
			double phiTest = phi;
			double imPhiTest = imPhi;
			double phiTest2 = testBin.x();
			double imPhiTest2 = testBin.y();
			phiTest = new Complex("p", 1, phiTest).phi();
			imPhiTest = new Complex("p", 1, imPhiTest).phi();
			phiTest2 = new Complex("p", 1, phiTest2).phi();
			imPhiTest2 = new Complex("p", 1, imPhiTest2).phi();
			Assert.assertTrue(Math.abs(phiTest - phiTest2) < diff || Math.abs(Math.abs(phiTest - phiTest2) - Math.PI) < diff);
			Assert.assertTrue(Math.abs(imPhiTest - imPhiTest2) < diff || Math.abs(Math.abs(phiTest - phiTest2) - Math.PI) < diff);
			
			// dual
			Hypercomplex dual = new Dual(phi, imPhi);
			Vector<Double> dualAngledVector = Vectors.vectorFromHypercomplexAngle(dual);
			Hypercomplex testDual = Hypercomplex.dual3DAngle(dualAngledVector);
			imPhiTest = imPhi;
			imPhiTest2 = testDual.y();
			phiTest2 = new Complex("p", 1, testDual.x()).phi();
			Assert.assertTrue(Math.abs(phiTest - phiTest2) < diff);
			Assert.assertTrue(Math.abs(imPhiTest - imPhiTest2) < diff);
			
			// complex
			Hypercomplex complex = new Complex(phi, imPhi);
			Vector<Double> complexAngledVector = Vectors.vectorFromHypercomplexAngle(complex);
			Hypercomplex testComplex = Hypercomplex.complex3DAngle(complexAngledVector);
			imPhiTest = imPhi;
			imPhiTest2 = testComplex.y();
			phiTest2 = new Complex("p", 1, testComplex.x()).phi();
			Assert.assertTrue(Math.abs(phiTest - phiTest2) < diff);
			Assert.assertTrue(Math.abs(imPhiTest - imPhiTest2) < diff);	
			
		}
	}

	@Test
	public void testHypercomplexAngles1() {
		double diff = 0.0001;
		boolean cpx = false, cnx = false, cpy = false, cny = false, cpz = false, cnz = false;
		boolean dpx = false, dnx = false, dpy = false, dny = false, dpz = false, dnz = false;
		boolean bpx = false, bnx = false, bpy = false, bny = false, bpz = false, bnz = false;
		for (double imPhi = -Math.PI; imPhi <= Math.PI; imPhi += Math.PI / 16) {
			for (double phi = -Math.PI; phi <= Math.PI; phi += Math.PI / 16) {
//				System.out.println("  phi == " + phi / Math.PI + " PI");
//				System.out.println("  imPhi == " + imPhi / Math.PI + " PI");
				Hypercomplex complex = new Complex(phi, imPhi);
				Vector<Double> complexAngledVector = Vectors.vectorFromHypercomplexAngle(complex);
				//System.out.print("comp: test.re() == " + test1.re() / Math.PI + " PI; ");
				//System.out.println("test.im() == " + test1.im() / Math.PI + " PI");
				if (complexAngledVector.get(0) < 0) {
					cnx = true;
				} else if (complexAngledVector.get(0) > 0) {
					cpx = true;
				}
				if (complexAngledVector.get(1) < 0) {
					cny = true;
				} else if (complexAngledVector.get(1) > 0) {
					cpy = true;
				}
				if (complexAngledVector.get(2) < 0) {
					cnz = true;
				} else if (complexAngledVector.get(2) > 0) {
					cpz = true;
				}
				/**
				 * complex 3D-length must be == sqrt(cosh²(imPhi) + sinh²(imPhi)) == sqrt(2 * sinh²(imPhi) + 1)
				 */
				Assert.assertTrue(Math.abs(Math.sqrt(Math.pow(Math.cosh(imPhi), 2) + Math.pow(Math.sinh(imPhi), 2)) - Vectors.length(complexAngledVector)) < diff);
				Assert.assertTrue(Math.abs(Math.sqrt(2 * Math.pow(Math.sinh(imPhi), 2) + 1) - Vectors.length(complexAngledVector)) < diff);
				Hypercomplex dual = new Dual(phi, imPhi);
				Vector<Double> dualAngledVector = Vectors.vectorFromHypercomplexAngle(dual);
				//System.out.print("dual: test.re() == " + test2.re() / Math.PI + " PI; ");
				//System.out.println("test.im() == " + test2.im() / Math.PI + " PI");
				if (dualAngledVector.get(0) < 0) {
					dnx = true;
				} else if (dualAngledVector.get(0) > 0) {
					dpx = true;
				}
				if (dualAngledVector.get(1) < 0) {
					dny = true;
				} else if (dualAngledVector.get(1) > 0) {
					dpy = true;
				}
				if (dualAngledVector.get(2) < 0) {
					dnz = true;
				} else if (dualAngledVector.get(2) > 0) {
					dpz = true;
				}
				/**
				 * dual 2D-length must be == 1
				 */
				Assert.assertTrue(Math.abs(Math.pow(dualAngledVector.get(0), 2) + Math.pow(dualAngledVector.get(1), 2) - 1d) < diff);
				/**
				 * dual 3D-length must be == Math.sqrt(Math.pow(imPhi, 2) + 1)
				 */
				Assert.assertTrue(Math.abs(Math.sqrt(Math.pow(imPhi, 2) + 1) - Vectors.length(dualAngledVector)) < diff);
				Hypercomplex binary = new Binary(phi, imPhi);
				Vector<Double> binaryAngledVector = Vectors.vectorFromHypercomplexAngle(binary);
//				System.out.println("angle(x, y) == " + new Complex(binaryAngledVector.get(0), binaryAngledVector.get(1)).phi() / Math.PI + " PI; ");
//				System.out.println("angle(x, -z) == " + new Complex(binaryAngledVector.get(0), -binaryAngledVector.get(2)).phi() / Math.PI + " PI; ");
				if (binaryAngledVector.get(0) < 0) {
					bnx = true;
				} else if (binaryAngledVector.get(0) > 0) {
					bpx = true;
				}
				if (binaryAngledVector.get(1) < 0) {
					bny = true;
				} else if (binaryAngledVector.get(1) > 0) {
					bpy = true;
				}
				if (binaryAngledVector.get(2) < 0) {
					bnz = true;
				} else if (binaryAngledVector.get(2) > 0) {
					bpz = true;
				}
				/**
				 * binary 3D-length must be == 1
				 */
				Assert.assertTrue(Vectors.length(binaryAngledVector) - 1d < diff);
			}
		}
		/**
		 * complex angled vectors need to be not just purely positive or negative in either x-, y- or z-direction
		 */
		Assert.assertTrue(cpx && cnx && cpy && cny && cpz && cnz);
		/**
		 * dual angled vectors need to be not just purely positive or negative in either x-, y- or z-direction
		 */
		Assert.assertTrue(dpx && dnx && dpy && dny && dpz && dnz);
		/**
		 * binary angled vectors need to be not just purely positive or negative in either x-, y- or z-direction
		 */
		Assert.assertTrue(bpx && bnx && bpy && bny && bpz && bnz);
	}

}
