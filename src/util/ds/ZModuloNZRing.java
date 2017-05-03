package util.ds;

import java.util.ArrayList;

// Wenn n prim ist, dann ist der Ring auch ein Körper
public class ZModuloNZRing {
	
	private int n;
	private ArrayList<Restklasse> restklassen;

	public ZModuloNZRing(int n) {
		this.n = n;
		restklassen = new ArrayList<Restklasse>();
		for (int i = 0; i < n; ++i) {
			restklassen.add(new Restklasse(this, i));
		}
	}
	
	public int getN() {
		return n;
	}
	
	public ArrayList<Restklasse> getRestklassen() {
		return restklassen;
	}
	
	public void printPlusTabelle() {
		int maxLength = getRestklassen().get(getN() - 1).toString().length();
		for (int zeile = -1; zeile < getN(); ++zeile) {
			for (int spalte = -1; spalte < getN(); ++spalte) {
				if (spalte == -1) {
					if (zeile == -1) {
						System.out.print(" ");
						for (int i = 0; i < maxLength - 1; ++i) {
							if (i == maxLength / 2) {
								System.out.print("+");
							}
							System.out.print(" ");
						}
						System.out.print(" |");
					} else {
						if (zeile == 0) {
							for (int i = 0; i < maxLength + 2; ++i) {
								System.out.print("-");
							}
							System.out.print("+");
							for (int i = 0; i < (maxLength + 1) * getN(); ++i) {
								System.out.print("-");
							}
							System.out.println();
						}
						System.out.print(" " + getRestklassen().get(zeile) + " |");
					}
				} else {
					if (zeile == -1) {
						System.out.print(" " + getRestklassen().get(spalte));
					} else {
						System.out.print(" " + getRestklassen().get(zeile).plus(getRestklassen().get(spalte)));
					}
				}
			}
			System.out.println();
		}
	}
	
	public void printMalTabelle() {
		int maxLength = getRestklassen().get(getN() - 1).toString().length();
		for (int zeile = -1; zeile < getN(); ++zeile) {
			for (int spalte = -1; spalte < getN(); ++spalte) {
				if (spalte == -1) {
					if (zeile == -1) {
						System.out.print(" ");
						for (int i = 0; i < maxLength - 1; ++i) {
							if (i == maxLength / 2) {
								System.out.print("*");
							}
							System.out.print(" ");
						}
						System.out.print(" |");
					} else {
						if (zeile == 0) {
							for (int i = 0; i < maxLength + 2; ++i) {
								System.out.print("-");
							}
							System.out.print("+");
							for (int i = 0; i < (maxLength + 1) * getN(); ++i) {
								System.out.print("-");
							}
							System.out.println();
						}
						System.out.print(" " + getRestklassen().get(zeile) + " |");
					}
				} else {
					if (zeile == -1) {
						System.out.print(" " + getRestklassen().get(spalte));
					} else {
						System.out.print(" " + getRestklassen().get(zeile).mal(getRestklassen().get(spalte)));
					}
				}
			}
			System.out.println();
		}
	}

	@Override
	public String toString() {
		StringBuffer buf = new StringBuffer();
		buf.append("Z/" + n + "Z = {");
		if (getRestklassen() != null && getRestklassen().size() > 0) {
			buf.append(getRestklassen().get(0));
		}
		for (int i = 1; i < n; ++i) {
			buf.append(", " + getRestklassen().get(i));
		}
		buf.append("}");
		return buf.toString();
	}

}
