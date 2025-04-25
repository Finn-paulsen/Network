import os
import sys
from datetime import datetime, timedelta
from flask import Flask
from app import app, db
from models import User, Suspect, CriminalRecord, WantedNotice, DDOSTarget, DDOSAttackLog

def load_test_data():
    """
    Lädt Testdaten in die Datenbank.
    Diese Funktion sollte nur einmal ausgeführt werden, um die Datenbank mit Beispieldaten zu füllen.
    """
    print("Starte das Laden der Testdaten...")
    
    # Prüfe, ob bereits Daten vorhanden sind
    if Suspect.query.count() > 0:
        print("Die Datenbank enthält bereits Verdächtige. Überspringe das Laden der Testdaten.")
        return
    
    if DDOSTarget.query.count() > 0:
        print("Die Datenbank enthält bereits DDoS-Ziele. Überspringe das Laden der Testdaten.")
        return
    
    # Erstelle Beispiel-Verdächtige
    suspects = [
        {
            'first_name': 'Alexander',
            'last_name': 'Schmidt',
            'alias': 'BlackShadow',
            'nationality': 'Deutsch',
            'date_of_birth': datetime(1985, 3, 15),
            'gender': 'Männlich',
            'height': 182,
            'weight': 78,
            'eye_color': 'Blau',
            'hair_color': 'Braun',
            'last_known_location': 'Berlin, Deutschland',
            'threat_level': 4,
            'status': 'Active',
            'photo_url': 'suspect1.svg',
            'criminal_records': [
                {
                    'crime': 'Bankbetrug',
                    'description': 'Durchführung mehrerer elektronischer Banküberweisungen durch Schadsoftware',
                    'date_committed': datetime(2019, 6, 10),
                    'location': 'Frankfurt, Deutschland',
                    'jurisdiction': 'Deutschland',
                    'status': 'Convicted',
                    'sentence': '5 Jahre Haft'
                },
                {
                    'crime': 'Identitätsdiebstahl',
                    'description': 'Diebstahl persönlicher Daten von mehr als 50.000 Personen durch Phishing',
                    'date_committed': datetime(2018, 3, 5),
                    'location': 'München, Deutschland',
                    'jurisdiction': 'Deutschland',
                    'status': 'Convicted',
                    'sentence': '3 Jahre Haft (zur Bewährung ausgesetzt)'
                }
            ],
            'wanted_notices': [
                {
                    'notice_type': 'Red',
                    'issuing_country': 'Deutschland',
                    'charge': 'Internationale Geldwäsche',
                    'details': 'Verdächtigt, ein internationales Netzwerk zur Geldwäsche mit Kryptowährungen betrieben zu haben',
                    'date_issued': datetime(2022, 1, 15),
                    'expiration_date': datetime(2025, 1, 15),
                    'reward_amount': 50000,
                    'contact_info': 'Interpol Berlin: +49-30-123456789',
                    'is_active': True
                }
            ]
        },
        {
            'first_name': 'Ivan',
            'last_name': 'Petrov',
            'alias': 'CyberPhantom',
            'nationality': 'Russisch',
            'date_of_birth': datetime(1990, 8, 22),
            'gender': 'Männlich',
            'height': 175,
            'weight': 72,
            'eye_color': 'Grün',
            'hair_color': 'Schwarz',
            'last_known_location': 'Moskau, Russland',
            'threat_level': 5,
            'status': 'Active',
            'photo_url': 'suspect2.svg',
            'criminal_records': [
                {
                    'crime': 'Cyberspionage',
                    'description': 'Hacking staatlicher Einrichtungen mehrerer europäischer Länder',
                    'date_committed': datetime(2020, 11, 15),
                    'location': 'Unbekannt',
                    'jurisdiction': 'International',
                    'status': 'Alleged',
                    'sentence': 'Ausstehend'
                },
                {
                    'crime': 'Ransomware-Angriffe',
                    'description': 'Entwicklung und Verbreitung der "CryptoLock" Ransomware',
                    'date_committed': datetime(2021, 2, 28),
                    'location': 'Unbekannt',
                    'jurisdiction': 'International',
                    'status': 'Alleged',
                    'sentence': 'Ausstehend'
                },
                {
                    'crime': 'DDoS-Angriffe',
                    'description': 'Durchführung von DDoS-Angriffen auf kritische Infrastruktur',
                    'date_committed': datetime(2020, 5, 10),
                    'location': 'Multiple',
                    'jurisdiction': 'International',
                    'status': 'Alleged',
                    'sentence': 'Ausstehend'
                }
            ],
            'wanted_notices': [
                {
                    'notice_type': 'Red',
                    'issuing_country': 'Vereinigte Staaten',
                    'charge': 'Computerbetrug und Spionage',
                    'details': 'Verdächtigt, Teil einer staatlich unterstützten Hackergruppe zu sein, die für mehrere globale Cyberangriffe verantwortlich ist',
                    'date_issued': datetime(2021, 7, 10),
                    'expiration_date': datetime(2026, 7, 10),
                    'reward_amount': 1000000,
                    'contact_info': 'FBI Cyber Division: +1-202-555-0123',
                    'is_active': True
                }
            ]
        },
        {
            'first_name': 'Emma',
            'last_name': 'Zhang',
            'alias': 'PhoenixByte',
            'nationality': 'Kanadisch',
            'date_of_birth': datetime(1988, 12, 5),
            'gender': 'Weiblich',
            'height': 165,
            'weight': 58,
            'eye_color': 'Braun',
            'hair_color': 'Schwarz',
            'last_known_location': 'Toronto, Kanada',
            'threat_level': 3,
            'status': 'Active',
            'photo_url': 'suspect3.svg',
            'criminal_records': [
                {
                    'crime': 'Banktrojaner-Entwicklung',
                    'description': 'Entwicklung und Verteilung des "GhostBank" Trojaners',
                    'date_committed': datetime(2018, 9, 3),
                    'location': 'Vancouver, Kanada',
                    'jurisdiction': 'Kanada',
                    'status': 'Convicted',
                    'sentence': '2 Jahre Haft'
                },
                {
                    'crime': 'Zero-Day-Exploit-Handel',
                    'description': 'Verkauf von Zero-Day-Exploits auf dem Schwarzmarkt',
                    'date_committed': datetime(2020, 4, 15),
                    'location': 'Unbekannt',
                    'jurisdiction': 'International',
                    'status': 'Alleged',
                    'sentence': 'Ausstehend'
                }
            ],
            'wanted_notices': [
                {
                    'notice_type': 'Yellow',
                    'issuing_country': 'Kanada',
                    'charge': 'Cyberkriminalität',
                    'details': 'Gesuchte Person mit Verbindungen zu Darknet-Märkten und Hacking-Gruppen',
                    'date_issued': datetime(2021, 3, 20),
                    'expiration_date': datetime(2024, 3, 20),
                    'reward_amount': 25000,
                    'contact_info': 'RCMP Cyber Crime Division: +1-416-555-7890',
                    'is_active': True
                }
            ]
        }
    ]
    
    # Füge Verdächtige zur Datenbank hinzu
    for suspect_data in suspects:
        criminal_records_data = suspect_data.pop('criminal_records', [])
        wanted_notices_data = suspect_data.pop('wanted_notices', [])
        
        suspect = Suspect(**suspect_data)
        db.session.add(suspect)
        db.session.flush()  # Um die ID zu erhalten
        
        # Füge Strafregister hinzu
        for record_data in criminal_records_data:
            record = CriminalRecord(suspect_id=suspect.id, **record_data)
            db.session.add(record)
        
        # Füge Fahndungsausschreibungen hinzu
        for notice_data in wanted_notices_data:
            notice = WantedNotice(suspect_id=suspect.id, **notice_data)
            db.session.add(notice)
    
    # Erstelle Beispiel-DDoS-Ziele
    targets = [
        {
            'target_name': 'Testserver Alpha',
            'target_url': 'https://test-server-alpha.example.com',
            'ip_address': '192.168.1.100',
            'port': 80,
            'protocol': 'HTTP',
            'target_type': 'Webserver',
            'vulnerability_level': 3,
            'country': 'Deutschland',
            'created_by': 1  # Annahme: User mit ID 1 existiert
        },
        {
            'target_name': 'Banking API',
            'target_url': 'https://api.banking-test.example.org',
            'ip_address': '10.0.5.25',
            'port': 443,
            'protocol': 'HTTPS',
            'target_type': 'API',
            'vulnerability_level': 2,
            'country': 'Schweiz',
            'created_by': 1
        },
        {
            'target_name': 'Game Server',
            'target_url': 'game.example.net',
            'ip_address': '203.0.113.42',
            'port': 27015,
            'protocol': 'TCP',
            'target_type': 'Gaming',
            'vulnerability_level': 4,
            'country': 'USA',
            'created_by': 1
        },
        {
            'target_name': 'IoT Device Hub',
            'target_url': 'https://iot-hub.example.io',
            'ip_address': '198.51.100.73',
            'port': 8883,
            'protocol': 'MQTT',
            'target_type': 'IoT',
            'vulnerability_level': 5,
            'country': 'Kanada',
            'created_by': 1
        }
    ]
    
    # Füge DDoS-Ziele zur Datenbank hinzu
    for target_data in targets:
        target = DDOSTarget(**target_data)
        db.session.add(target)
        
        # Füge einige Beispiel-Angriffslogs hinzu
        log = DDOSAttackLog(
            target_id=1,  # Wird später aktualisiert
            attack_method='SYN Flood',
            packets_sent=10000000,
            bandwidth_used=1250.5,
            duration=60,
            attack_status='Completed',
            start_time=datetime.now() - timedelta(days=2, hours=3),
            end_time=datetime.now() - timedelta(days=2, hours=2),
            success_rate=87.5,
            notes='Simulierter Angriff zu Bildungszwecken',
            created_by=1
        )
        db.session.add(log)
    
    # Commit alle Änderungen
    db.session.commit()
    print("Testdaten erfolgreich geladen!")

if __name__ == '__main__':
    with app.app_context():
        load_test_data()