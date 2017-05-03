package util.hypercomplex.mechanism;

import java.util.ArrayList;
import java.util.Vector;

import util.basics.Vectors;

/**
 * 
 * Hyper-complex mechanism. The mechanism consists of 
 * 
 * @author hoechp
 *
 */
public class Mechanism {

	private Mechanism previous;
	private Joint hypercomplexVector;
	private Joint adjustedHypercomplexVector;
	private ArrayList<Mechanism> attachements;

	public Mechanism() {
		this(null, new Joint());
	}
	
	public Mechanism(Mechanism prev) {
		this(prev, new Joint());
	}
	
	public Mechanism(Joint vec) {
		this(null, vec);
	}

	public Mechanism(Mechanism prev, Joint vec) {
		previous = prev;
		hypercomplexVector = new Joint(vec);
		if (prev != null) {
			prev.getAttachements().add(this);
		}
		attachements = new ArrayList<Mechanism>();
		updateData();
	}
	
	/**
	 * this function must be called for changes in this mechanism and its sub-mechanisms to take effect.
	 */
	public void updateData() {
		adjustedHypercomplexVector = new Joint(hypercomplexVector);
		if (previous != null) {
			putOn(this, previous);
			//putOn(adjustedHypercomplexVector, previous.getAdjustedHypercomplexVector());
			adjustedHypercomplexVector.setPos(Vectors.plus(adjustedHypercomplexVector.getPos(), previous.getAdjustedJoint().getVec()));
		}
		for (Mechanism m: attachements) {
			m.updateData();
		}
	}

	public static void putOn(Mechanism m1, Mechanism m2) {
		Joint h1 = m1.getAdjustedJoint();
		Joint h2 = m2.getAdjustedJoint();
		h1.setNormal(Vectors.toNormalAndCompare(h1.getNormal(), h2.getNormal(), h2.getCompare()));
		h1.setCompare(Vectors.toNormalAndCompare(h1.getCompare(), h2.getNormal(), h2.getCompare()));
		h1.setPos(Vectors.toNormalAndCompare(h1.getPos(), h2.getNormal(), h2.getCompare()));
		if (h2.isAxis()) {
			double angle = h2.getAngle().real();
			h1.setNormal(Vectors.turnedAroundNormal(h1.getNormal(), h2.getNormal(), angle));
			h1.setCompare(Vectors.turnedAroundNormal(h1.getCompare(), h2.getNormal(), angle));
			h1.setPos(Vectors.turnedAroundNormal(h1.getPos(), h2.getNormal(), angle));
		} else {
			Vector<Double> comp = h2.getCompare();
			Vector<Double> v = Vectors.minus(h2.getVec(), h2.getPos());
			if (Vectors.equals(Vectors.partOrthogonalTo(v, comp), Vectors.zero3D(), 0d))  {
				double temp = h2.getReal();
				if (temp == 0) {
					h2.setReal(1);
				} else {
					h2.setReal(temp * 2);
				}
				v = Vectors.minus(h2.getVec(), h2.getPos());
				if (Vectors.equals(Vectors.partOrthogonalTo(v, comp), Vectors.zero3D(), 0d))  {
					h2.setReal(temp);
					return;
				}
				h2.setReal(temp);
			}
			Vector<Double> rotNorm = Vectors.cross(comp, v);
			Vector<Double> rotComp = Vectors.cross(rotNorm, comp);
			if (Vectors.equals(rotNorm, Vectors.zero3D(), 0)) {
				if (Math.max(Vectors.length(comp), Vectors.length(v)) > Vectors.length(Vectors.plus(comp, v))) {
					h1.setNormal(Vectors.times(h1.getNormal(), -1));
					h1.setCompare(Vectors.times(h1.getCompare(), -1));
					h1.setPos(Vectors.times(h1.getPos(), -1));
				}
				return;
			}
			double angleV = Vectors.realAngleAroundNormalWithCompare(v, rotNorm, rotComp);
			double angleC = Vectors.realAngleAroundNormalWithCompare(comp, rotNorm, rotComp);
			double angle = angleV - angleC;
			h1.setNormal(Vectors.turnedAroundNormal(h1.getNormal(), rotNorm, angle));
			h1.setCompare(Vectors.turnedAroundNormal(h1.getCompare(), rotNorm, angle));
			h1.setPos(Vectors.turnedAroundNormal(h1.getPos(), rotNorm, angle));
			
			
			
			/**
			 * usually normal and compare are z and x. angle of zero produces vector of x.
			 * now the position of v := Vectors.minus(getVec(), getPos()) instead of being at getCompare(),
			 * determines in what direction and how far the usual normal and compare are rotated to obtain the new base
			 * 
			 * the normal of the rotation is Vectors.cross(x, v).
			 * angle is the angle of v along that normal with any compare vector.
			 * 
			 * then measure the angle of the compare along that rotationNormal and rotationCompare
			 * then turn normal and compare by angle_v - angle_compare along that rotationNormal
			 */
/*			Vector<Double> comp = h2.getCompare();
			Vector<Double> v = Vectors.minus(h2.getVec(), h2.getPos());
			if (Vectors.equals(Vectors.partOrthogonalTo(v, comp), Vectors.zero3D(), 0d))  {
				double temp = h2.getReal();
				if (temp == 0) {
					h2.setReal(1);
				} else {
					h2.setReal(temp * 2);
				}
				v = Vectors.minus(h2.getVec(), h2.getPos());
				if (Vectors.equals(Vectors.partOrthogonalTo(v, comp), Vectors.zero3D(), 0d))  {
					h2.setReal(temp);
					return;
				}
				h2.setReal(temp);
			}
			Vector<Double> rotNorm = Vectors.cross(comp, v);
			Vector<Double> rotComp = Vectors.cross(rotNorm, comp);
			if (Vectors.equals(rotNorm, Vectors.zero3D(), 0)) {
				if (Math.max(Vectors.length(comp), Vectors.length(v)) > Vectors.length(Vectors.plus(comp, v))) {
					h1.setNormal(Vectors.times(h1.getNormal(), -1));
					h1.setCompare(Vectors.times(h1.getCompare(), -1));
					h1.setPos(Vectors.times(h1.getPos(), -1));
				}
				return;
			}
			double angleV = Vectors.realAngleAroundNormalWithCompare(v, rotNorm, rotComp);
			double angleC = Vectors.realAngleAroundNormalWithCompare(comp, rotNorm, rotComp);
			double angle = angleV - angleC;
			h1.setNormal(Vectors.turnedAroundNormal(h1.getNormal(), rotNorm, angle));
			h1.setCompare(Vectors.turnedAroundNormal(h1.getCompare(), rotNorm, angle));
			h1.setPos(Vectors.turnedAroundNormal(h1.getPos(), rotNorm, angle));
*/
		}
	}
	
	public Joint getJoint() {
		return hypercomplexVector;
	}

	public void setJoint(Joint hypercomplexVector) {
		this.hypercomplexVector = hypercomplexVector;
	}

	public ArrayList<Mechanism> getAttachements() {
		return attachements;
	}

	public void setAttachements(ArrayList<Mechanism> attachements) {
		this.attachements = attachements;
	}

	public Joint getAdjustedJoint() {
		return adjustedHypercomplexVector;
	}

	public void setAdjustedJoint(Joint adjustedHypercomplexVector) {
		this.adjustedHypercomplexVector = adjustedHypercomplexVector;
	}

	public Mechanism getPrevious() {
		return previous;
	}

	public void setPrevious(Mechanism previous) {
		this.previous = previous;
	}
	
}
