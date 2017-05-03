package util.hypercomplex.mechanism;

public class Freedom {

	private boolean inverted = false;
	private boolean periodic = false;
	private double percentage = 0.5;
	private double factor = 1;
	private double minVal = 0;
	
	public Freedom() {
	}

	public Freedom(boolean periodic, double percentage, double factor, double minVal) {
		this.periodic = periodic;
		this.percentage = percentage;
		this.factor = factor;
		this.minVal = minVal;
		normalizePercentage();
	}
	
	public double getValue() {
		return getPercentage() * factor + minVal;
	}
	
	public void addPercentage(double percentage) {
		this.percentage = this.percentage + (inverted ? -1 : 1) * percentage;
		normalizePercentage();
	}
	
	private void normalizePercentage() {
		if (periodic) {
			if (percentage > 1 || percentage < 0) {
				percentage = percentage - Math.floor(percentage);
			}
		} else {
			if (percentage < 0) {
				percentage = 0;
			} else if (percentage > 1) {
				percentage = 1;
			}
		}
	}
	
	public void invert() { // mirror
		this.minVal = -(minVal + factor);
		percentage = 1 - percentage;
		inverted = !inverted;
	}
	public void negate() { // just change direction
		inverted = !inverted;
	}
	
	public boolean isPeriodic() {
		return periodic;
	}
	public void setPeriodic(boolean periodic) {
		this.periodic = periodic;
	}
	public double getPercentage() {
		return percentage;
	}
	public void setPercentage(double percentage) {
		this.percentage = inverted ? (1 - percentage) : percentage;
		normalizePercentage();
	}
	public double getFactor() {
		return factor;
	}
	public void setFactor(double factor) {
		this.factor = factor;
	}
	public double getMinVal() {
		return minVal;
	}
	public void setMinVal(double minVal) {
		this.minVal = minVal;
	}
	
}
