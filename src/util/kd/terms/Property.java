package util.kd.terms;

public class Property {

	private String name;
	private int id;
	
	public Property(int id) {
		this.name = null;
		this.id = id;
	}
	
	public Property(String name, int id) {
		this.name = name;
		this.id = id;
	}

	public String getName() {
		return name;
	}

	public int getId() {
		return id;
	}
	
	public String toString() {
		if (name == null) {
			return ((Integer)id).toString();
		} else {
			return name;
		}
	}

}
