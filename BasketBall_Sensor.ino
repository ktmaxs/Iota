/**
 * Basketball Sensor Code
 * 
 * Uses IR to detect if a basketball has gone into the hoop and makes a sound if so.
 * Uses indirect IR, goes off if the IR is reflected off the ball and back into the sensor.
 * 
 * Author: Devon Verlangieri
 * Date: 2020-2021 Acedemic School Year
**/

// pins
#define     IR_LED                  0
#define     IR_SENSOR               2
#define     SPEAKER                 1
#define     BASKET_CHECK_SECONDS   0.1

// many, many notes to choose from for the speaker
#define NOTE_C4 262
#define NOTE_CS4 277
#define NOTE_D4 294
#define NOTE_DS4 311
#define NOTE_E4 330
#define NOTE_F4 349
#define NOTE_FS4 370
#define NOTE_G4 392
#define NOTE_GS4 415
#define NOTE_A4 440
#define NOTE_AS4 466
#define NOTE_B4 494
#define NOTE_C5 523
#define NOTE_CS5 554
#define NOTE_D5 587
#define NOTE_DS5 622
#define NOTE_E5 659
#define NOTE_F5 698
#define NOTE_FS5 740
#define NOTE_G5 784
#define NOTE_GS5 831
#define NOTE_A5 880
#define NOTE_AS5 932
#define NOTE_B5 988
#define NOTE_C6 1047
#define NOTE_CS6 1109
#define NOTE_D6 1175
#define NOTE_DS6 1245
#define NOTE_E6 1319
#define NOTE_F6 1397
#define NOTE_FS6 1480
#define NOTE_G6 1568
#define NOTE_GS6 1661
#define NOTE_A6 1760
#define NOTE_AS6 1865

///////////////////////////////////////////////////////
// Setup function
///////////////////////////////////////////////////////
void setup(void)
{
  // Set up input pins
  pinMode(IR_SENSOR, INPUT);
  
  // Set up output pins
  pinMode(IR_LED, OUTPUT);
  pinMode(SPEAKER, OUTPUT);
}

///////////////////////////////////////////////////////
// Loop Function
///////////////////////////////////////////////////////
void loop(void) 
{
  // checks if the sensor saw the basketball
  if (isBallInHoop()) 
  {  
    sound(250);
  }
  
  // Delay for 100 milliseconds so the ball in hoop check happens 10 times a second.
  delay(100); // can be changed for faster/slower operation if needed
}



///////////////////////////////////////////////////////
// isBallInHoop function
//
// Returns true if a ball reflects IR into the sensor.
///////////////////////////////////////////////////////
boolean isBallInHoop() 
{  
  // Pulse the IR LED at 38khz for 1 millisecond
  pulseIR(1000);

  // Check if the IR sensor picked up the pulse (i.e. output wire went to ground).
  if (digitalRead(IR_SENSOR) == LOW) {
    return true; 
  }

  return false; 
}

///////////////////////////////////////////////////////
// pulseIR function
//
// Pulses the IR LED at 38khz for the specified number
// of microseconds.
///////////////////////////////////////////////////////
void pulseIR(long microsecs) 
{
  // 38khz IR pulse function from Adafruit tutorial: http://learn.adafruit.com/ir-sensor/overview
  
  // we'll count down from the number of microseconds we are told to wait

  // got this code from online and it's worked fine without interrupts but I'll leave this here in case it causes problems in the future
  //cli();  // this turns off any background interrupts
 
  while (microsecs > 0)
  {
    // 38 kHz is about 13 microseconds high and 13 microseconds low
   digitalWrite(IR_LED, HIGH);  // this takes about 3 microseconds to happen
   delayMicroseconds(9);         // hang out for 10 microseconds, you can also change this to 9 if its not working
   digitalWrite(IR_LED, LOW);   // this also takes about 3 microseconds
   delayMicroseconds(9);         // hang out for 10 microseconds, you can also change this to 9 if its not working
 
   // so 26 microseconds altogether
   microsecs -= 26;
  }

  // again with the interrupts...
  //sei();  // this turns them back on
}

///////////////////////////////////////////////////////
// sound function
//
// Plays a sequence of 3 tones on the speaker.
// Honestly this function could be written a lot nicer
///////////////////////////////////////////////////////
void sound(uint32_t milliseconds)
{
  // this can be edited to play any sequence of notes
  // this particular sequence was chosen at random 
  // I had a hard time getting the speaker to play at full volume, 
  // notes around these frequencies seemed to be the loudest
  tone(SPEAKER, NOTE_D5);
  delay(milliseconds);
  tone(SPEAKER, NOTE_E5);
  delay(milliseconds - 150);
  tone(SPEAKER, NOTE_A5);
  delay(milliseconds);
  noTone(SPEAKER);
}
