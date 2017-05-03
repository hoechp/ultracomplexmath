package util.hypercomplex.mechanism;

import java.util.HashMap;

import util.hypercomplex.Complex;

public class Actor {

	private Joint joint;
	private Joint original;
	private Freedom stretchFreedom = null;
	private Freedom rollFreedom = null;
	private Freedom turnFreedom = null;
	private Freedom elevateFreedom = null;
	private Freedom realAngleFreedom = null;
	private Freedom imaginaryAngleFreedomFreedom = null;
	private HashMap<String, Freedom> map = new HashMap<String, Freedom>();

	public Actor(Joint joint) {
		this.joint = joint;
		original = new Joint(joint); 
	}
	
	public Actor(Mechanism mechanism) {
		joint = mechanism.getJoint();
		original = new Joint(joint); 
	}
	
	public void act() {
		if (rollFreedom != null || turnFreedom != null || elevateFreedom != null) {
			joint.setNormal(original.getNormal());
			joint.setCompare(original.getCompare());
		}
		if (rollFreedom != null) {
			joint.roll(rollFreedom.getValue());
		}
		if (turnFreedom != null) {
			joint.turn(turnFreedom.getValue());
		}
		if (elevateFreedom != null) {
			joint.elevate(elevateFreedom.getValue());
		}
		if (stretchFreedom != null) {
			joint.setReal(stretchFreedom.getValue());
		}
		if (realAngleFreedom != null) {
			joint.setAngle(joint.getAngle().times(0).plus(new Complex(realAngleFreedom.getValue(), joint.getAngle().imaginary())));
		}
		if (imaginaryAngleFreedomFreedom != null) {
			joint.setAngle(joint.getAngle().times(0).plus(new Complex(joint.getAngle().real(), imaginaryAngleFreedomFreedom.getValue())));
		}
	}
	
	public Freedom get(String key) {
		return map.get(key);
	}
	
	public HashMap<String, Freedom> freedoms() {
		return map;
	}

	public Joint getJoint() {
		return joint;
	}
	public void setJoint(Joint joint) {
		this.joint = joint;
	}
	public Freedom getStretchFreedom() {
		return stretchFreedom;
	}
	public void setStretchFreedom(Freedom stretchFreedom) {
		this.stretchFreedom = stretchFreedom;
		map.put("stretch", stretchFreedom);
	}
	public Freedom getRollFreedom() {
		return rollFreedom;
	}
	public void setRollFreedom(Freedom rollFreedom) {
		this.rollFreedom = rollFreedom;
		map.put("roll", rollFreedom);
	}
	public Freedom getTurnFreedom() {
		return turnFreedom;
	}
	public void setTurnFreedom(Freedom turnFreedom) {
		this.turnFreedom = turnFreedom;
		map.put("turn", turnFreedom);
	}
	public Freedom getElevateFreedom() {
		return elevateFreedom;
	}
	public void setElevateFreedom(Freedom elevateFreedom) {
		this.elevateFreedom = elevateFreedom;
		map.put("elevate", elevateFreedom);
	}
	public Freedom getRealAngleFreedom() {
		return realAngleFreedom;
	}
	public void setRealAngleFreedom(Freedom realAngleFreedom) {
		this.realAngleFreedom = realAngleFreedom;
		map.put("real angle", realAngleFreedom);
	}
	public Freedom getImaginaryAngleFreedomFreedom() {
		return imaginaryAngleFreedomFreedom;
	}
	public void setImaginaryAngleFreedomFreedom(Freedom imaginaryAngleFreedomFreedom) {
		this.imaginaryAngleFreedomFreedom = imaginaryAngleFreedomFreedom;
		map.put("imaginary angle", imaginaryAngleFreedomFreedom);
	}

}
