package util.hypercomplex.mechanism;

import java.util.ArrayList;
import java.util.Vector;

import util.basics.Vectors;
import util.hypercomplex.Binary;
import util.hypercomplex.Hypercomplex;

public class Joint {

	// private field data
	private Vector<Double> pos;
	private Vector<Double> normal; // just a direction
	private Vector<Double> compare; // just a direction
	private double real; // just a real
	private Hypercomplex angle;
	private boolean axis;

	// constructor
	public Joint() {
		pos = Vectors.zero3D();
		ArrayList<Vector<Double>> bases = Vectors.base3D();
		normal = bases.get(2);
		compare = bases.get(0);
		real = 1;
		angle = new Binary();
		axis = false;
	}
	
	// copy-constructor
	public Joint(Joint other) {
		pos = Vectors.copy(other.getPos());
		normal = Vectors.copy(other.getNormal());
		compare = Vectors.copy(other.getCompare());
		real = other.getReal();
		angle = other.getAngle().clone();
		axis = other.isAxis();
	}
	
	// method to calculate final point position
	public Vector<Double> getVec() {
		Vector<Double> vec = Vectors.toNormalAndCompare(Vectors.vectorFromHypercomplexAngle(angle), normal, compare);
		vec = Vectors.times(vec, real);
		return Vectors.plus(pos, vec);
	}

	// usual getter
	public Vector<Double> getPos() {
		return pos;
	}
	public Hypercomplex getAngle() {
		return angle;
	}
	public double getReal() {
		return real;
	}
	public Vector<Double> getNormal() {
		return normal;
	}
	public Vector<Double> getCompare() {
		return compare;
	}

	// usual setter
	public void setPos(Vector<Double> pos) {
		this.pos = pos;
	}
	public void setAngle(Hypercomplex angle) {
		this.angle = angle;
	}
	public void setReal(double real) {
		this.real = real;
	}
	public void setNormal(Vector<Double> normal) {
		this.normal = normal;
	}
	public void setCompare(Vector<Double> compare) {
		this.compare = compare;
	}

	public boolean isAxis() {
		return axis;
	}

	public void setAxis(boolean axis) {
		this.axis = axis;
	}
	
	public String toString() {
		return "HypercomplexJoint: " + pos + " + (" + real + " * vec(" + angle + ") along normal " + normal
				+ " and compare " + compare + ")";
		
	}
	
	// methods for direct manipulation
	
	public void switchMode() {
		axis = !axis;
	}
	
	public void shift(Vector<Double> add) {
		pos = Vectors.plus(pos, add);
	}
	
	public void stretch(double factor) {
		real *= factor;
	}

	public void addAngle(Hypercomplex angle) {
		this.angle = this.angle.plus(angle);
	}
	
	public void roll(double angle) {
		rot(Vectors.baseFromNormalAndCompare(normal, compare)[2], angle);
	}
	
	public void turn(double angle) {
		rot(Vectors.baseFromNormalAndCompare(normal, compare)[1], angle);
	}
	
	public void elevate(double angle) {
		rot(Vectors.baseFromNormalAndCompare(normal, compare)[0], angle);
	}
	
	public void rot(Vector<Double> normal, double angle) {
		this.normal = Vectors.turnedAroundNormal(this.normal, normal, angle);
		compare = Vectors.turnedAroundNormal(compare, normal, angle);
	}
	
}
