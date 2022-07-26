#include <Arduino_FreeRTOS.h>
#include <semphr.h>  // add the FreeRTOS functions for Semaphores (or Flags).

#define INCLUDE_vTaskSuspend                    1

// Declare a mutex Semaphore Handle which we will use to manage the Serial Port.
// It will be used to ensure only one Task is accessing this resource at any time.
SemaphoreHandle_t xSerialSemaphore;

// define two Tasks for DigitalRead & TiltSwitch
void TaskManualOverwrite( void *pvParameters );
void TaskTiltSwitch( void *pvParameters );
void TaskAlarm (void *pvParameters );


// Var
int alarm_on;

TaskHandle_t xTiltHandle = NULL;
TaskHandle_t xAlertHandle = NULL;

// the setup function runs once when you press reset or power the board
void setup() {
  pinMode(10, OUTPUT);
  pinMode(11, OUTPUT);
  pinMode(13, OUTPUT);
  pinMode(2, INPUT);
  
  
  // initialize serial communication at 9600 bits per second:
  Serial.begin(9600);
  
  while (!Serial) {
    ; // wait for serial port to connect. Needed for native USB, on LEONARDO, MICRO, YUN, and other 32u4 based boards.
  }

  // Semaphores are useful to stop a Task proceeding, where it should be paused to wait,
  // because it is sharing a resource, such as the Serial port.
  // Semaphores should only be used whilst the scheduler is running, but we can set it up here.
  if ( xSerialSemaphore == NULL )  // Check to confirm that the Serial Semaphore has not already been created.
  {
    xSerialSemaphore = xSemaphoreCreateMutex();  // Create a mutex semaphore we will use to manage the Serial Port
    if ( ( xSerialSemaphore ) != NULL )
      xSemaphoreGive( ( xSerialSemaphore ) );  // Make the Serial Port available for use, by "Giving" the Semaphore.
  }

  xTaskCreate(
    TaskTiltSwitch
    ,  "TiltSwitch" // A name just for humans
    ,  128  // Stack size
    ,  NULL //Parameters for the task
    ,  1  // Priority
    ,  &xTiltHandle ); //Task Handle

  xTaskCreate(
    TaskManualOverwrite
    , "ManualOverwrite"
    , 128
    , NULL
    , 2
    , NULL);

  xTaskCreate(
    TaskAlarm
    , "Alarm"
    , 128
    , NULL
    , 1
    , &xAlertHandle);

  // Now the Task scheduler, which takes over control of scheduling individual Tasks, is automatically started.
}

void loop()
{
  // Empty. Things are done in Tasks.
}

/*--------------------------------------------------*/
/*---------------------- Tasks ---------------------*/
/*--------------------------------------------------*/

void TaskTiltSwitch( void *pvParameters __attribute__((unused)) )  // This is a Task.
{

  for (;;)
  {
    // read the input on analog pin 0:
    int sensorValue = analogRead(A1);

    // See if we can obtain or "Take" the Serial Semaphore.
    // If the semaphore is not available, wait 5 ticks of the Scheduler to see if it becomes free.
    if ( xSemaphoreTake( xSerialSemaphore, ( TickType_t ) 5 ) == pdTRUE )
    {
      // We were able to obtain or "Take" the semaphore and can now access the shared resource.
      // We want to have the Serial Port for us alone, as it takes some time to print,
      // so we don't want it getting stolen during the middle of a conversion.
      // print out the value you read:
      if ( sensorValue < 1000 && alarm_on != 1) {
        alarm_on = 1;
        Serial.println("ALERT");
        digitalWrite(11, HIGH);
      }

      xSemaphoreGive( xSerialSemaphore ); // Now free or "Give" the Serial Port for others.
    }

    vTaskDelay(15);  // one tick delay (15ms) in between reads for stability
  }
}

void TaskManualOverwrite( void *pvParameters __attribute__((unused)) )  // This is a Task.
{
  for (;;)
  {
    int overwriteState = digitalRead(2);

    if ( xSemaphoreTake( xSerialSemaphore, ( TickType_t ) 5 ) == pdTRUE )
    {    
      if (overwriteState == LOW) {}

      else if (overwriteState == HIGH && alarm_on == 1) {
        Serial.println("FIXED");
        digitalWrite(11, LOW);

        while(digitalRead(4) == LOW) {
          vTaskSuspend(xTiltHandle);
        }

        // Use LED to indicate that reset is complete
        int LED_ON = 0;
        for (int i = 1; i <= 26; ++i) {
           if (LED_ON == 0) {
              digitalWrite(10, HIGH);
              LED_ON = 1;
           }
           else {
            digitalWrite(10, LOW);
            LED_ON = 0;
           }  
           delay(100);
        }

        // Turn of ALARM_LED
        alarm_on = 0;
        
        Serial.println("Reset Complete");
        // Resume the Tilt-switch task
        vTaskResume(xTiltHandle);
      }

    
    
    xSemaphoreGive( xSerialSemaphore );
    }

    vTaskDelay(15);
  }
}



void TaskAlarm( void *pvParameters __attribute__((unused)) )  // This is a Task.
{
  
  // The alarm ranges from tones 0 to 180, using a sinus, start at 0
  int alarmValue = 0;
  int toneVal;
  int sinVal;
  for (;;) // A Task shall never return or exit.
  {
    if (alarm_on == 1) {
      sinVal = (sin(alarmValue * (3.1412 / 180)));
      toneVal = 2000 + (int(sinVal * 1000));
      tone(8, toneVal);
      alarmValue++;

      if (alarmValue >= 180) {
        alarmValue = 0;
      }
    }
    else {
      noTone(8);
    }

    vTaskDelay(15);  // one tick delay (15ms) in between reads for stability
  }
}



