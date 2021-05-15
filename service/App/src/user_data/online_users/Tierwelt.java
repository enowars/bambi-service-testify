import java.util.ArrayList;
import java.util.Scanner;

public class Tierwelt {
	
	final static String filename = "Tiere.txt";
	final static String verz = "Projekt";
	
	public Tierwelt() {
	
		// ToDo: Initialisierung ArrayList tiere mit Vogel, Hund, Großkatze und Fisch 
		// Erstelle einen Besitzer mit zwei Haustieren und lasse dir die alle Infoa des Besitzers ausgeben.
		
		
		
		
		run();
	}
	
	public void run() {
		Utils.printInfo(tiere);
		
		insert();
		Utils.printInfo(tiere);
		
		sort();
		Utils.printInfo(tiere);
		
		printTier("Großkatze");
		
		remove("klasse","Hund");
		Utils.printInfo(tiere);
		
		remove("art","Jagdhund");
		Utils.printInfo(tiere);

		
		writeTiereToFile();
		System.out.println();
		
		ArrayList<Tier> tierList = new ArrayList<>();
		tierList = readTiereFromFile();
		Utils.printInfo(tierList);
	
	}
		
	// schreiben Tiere in Datei
	public void writeTiereToFile() {
		Utils.schreibeDatenObjekt(tiere, verz, filename);
		System.out.println();
	}

	// lesen Tiere aus Datei
	public ArrayList<Tier> readTiereFromFile() {
		ArrayList<Tier> tiere = Utils.leseDatenObjekt(verz, filename);
		return tiere;
	}
	
	// Tier hinzufügen
	public void insert() {
		Utils.insert(tiere);
	}
	
	// Tier nach Art oder Klasse löschen
	public void remove(String kriterium) {
		System.out.println("Nach welchem Kriterium soll ein Tier bzw. Tiere entfernt werden (Art/Klasse)");
		Scanner scan = new Scanner(System.in);
		if(scan.equals("Art"))
			//tier nach art löschen
			Utils.removeArt(tiere,kriterium);
		else
			//tier nach klasse löschen
			Utils.removeKlasse(tiere, kriterium);
	}
	
	// Tier nach Klasse sortieren
	public void sort() {
		Utils.sort(tiere);
	}
	
	// gibt Informtionen von einem bestimmten Tier aus 
	public void printTier(String tier) {
		Utils.printTier(tier, tiere);
	}

	public static void main(String[] args) {
		new Tierwelt();
	}
}
