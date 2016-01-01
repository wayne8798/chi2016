var imgName;
var imgWidth;
var imgHeight;

var hitStartTime;
var annoStartTime;
var annoEndTime;
var opsCount = 0;
var typingTimer;
var doneTypingInterval = 1000;
var pauseCount = 0;
var delCount = 0;

var annotationFlag = false;
var delFlag = false;

var prevStroke;
var eventLogs = [];

function logAction(action, param) {
  console.log(action);
  if (typeof param === "undefined") {
    eventLogs.push([(new Date()).getTime(), action]);
  }
  else {
    eventLogs.push([(new Date()).getTime(), action, param])
  }
}

$(document).ready(function() {
  // var task_params = document.getElementById("survey").href.substring(56).toString();
  // (new Image).src = 'http://128.174.241.28:8080/?' + task_params;

  hitStartTime = (new Date()).getTime();
  logAction("init");

  $(window).focus(function() {
    logAction("focus");
  });

  $(window).blur(function() {
    logAction("blur");
  });
  
  // document.getElementById("survey").href += "&worker_id=" +
  //  getParameterByName("workerId");

  imgName = document.getElementById("picture").name;
  
  if (imgName == "parkland") {
    imgWidth = 819;
    imgHeight = 630;
  }
  else if (imgName == "evite"){
    imgWidth = 891;
    imgHeight = 595;
  }
  else {
    imgWidth = 1139;
    imgHeight = 596;
  }

  $("#overlay").css("width", imgWidth);
  $("#overlay").css("height", imgHeight);
  $("#picture").css("width", imgWidth);
  $("#picture").css("height", imgHeight);

  var sketchpad = Raphael.sketchpad("editor", {
    width: imgWidth,
    height: imgHeight,
    editing: true
  });

      // Initialize the pen stroke (Thin Red)
      sketchpad.pen().width(6);
      sketchpad.pen().opacity(0.5);
      sketchpad.pen().color("#f00");

      // When the sketchpad changes, update the input field.
      sketchpad.change(function() {
        $("#strokes").val(sketchpad.json());
        opsCount ++;
      });

      $("#editor_undo").click(function() {
        sketchpad.undo();
        logAction("undo");
      });

      $("#editor_redo").click(function() {
        sketchpad.redo();
        logAction("redo");
      });

      $("#editor_clear").click(function() {
        sketchpad.clear();
        logAction("clear");
      });

      function changeToRed() {
        sketchpad.pen().color("#f00");
        document.getElementById("radio_red").src = "http://i.imgur.com/O21t3tT.png";
        document.getElementById("radio_yellow").src = "http://i.imgur.com/4bf1tFr.png";
        document.getElementById("radio_blue").src = "http://i.imgur.com/4bf1tFr.png";
        opsCount ++;

        logAction("red");
      }
      $("#radio_red").click(changeToRed);
      $('#editor_red').click(changeToRed);

      function changeToYellow() {
        sketchpad.pen().color("#ff0");
        document.getElementById("radio_red").src = "http://i.imgur.com/4bf1tFr.png";
        document.getElementById("radio_yellow").src = "http://i.imgur.com/O21t3tT.png";
        document.getElementById("radio_blue").src = "http://i.imgur.com/4bf1tFr.png";
        opsCount ++;

        logAction("yellow");
      }
      $("#radio_yellow").click(changeToYellow);
      $("#editor_yellow").click(changeToYellow);

      function changeToBlue() {
        sketchpad.pen().color("#00f");
        document.getElementById("radio_red").src = "http://i.imgur.com/4bf1tFr.png";
        document.getElementById("radio_yellow").src = "http://i.imgur.com/4bf1tFr.png";
        document.getElementById("radio_blue").src = "http://i.imgur.com/O21t3tT.png";
        opsCount ++;

        logAction("blue");
      }
      $("#radio_blue").click(changeToBlue);
      $("#editor_blue").click(changeToBlue);
    });

function startAnnotation() {
  if (annotationFlag == false) {
    $("#overlay").css("visibility","hidden");
    $("#control_panel").css("visibility", "visible");
    $("#task_start").css("color","#AEAEAE");
    $("#task_start").css("background-color","#DFDFDF")
    $("#task_start").css("cursor","default");
    $("#task_end").css("background-color","#FF0000");
    $("#task_end").css("cursor","pointer");

    annoStartTime = (new Date()).getTime();
    window.scrollTo(0, 450);
    annotationFlag = true;

    logAction("start");
  }
}

function endMarking() {
  /* wait until the stroke updating is finished. */
  setTimeout(function(e){
    var strokes = JSON.parse(document.getElementById("strokes").value);
    var last_stroke = JSON.stringify(strokes.pop());
    if ((typeof last_stroke !== "undefined") &&
      (typeof prevStroke === "undefined" ||
      prevStroke != last_stroke)) {
      logAction("stroke", last_stroke);
      prevStroke = last_stroke;
    }
  }, 100);
}

function onTextKeyUp() {
  clearTimeout(typingTimer);
  typingTimer = setTimeout(recordPause, doneTypingInterval);
  logAction("text_update", document.getElementById("text").value);
}

function onTextKeyDown(e) {
  clearTimeout(typingTimer);
  var unicode = e.keyCode ? e.keyCode : e.charCode;
  if (unicode == 8 || unicode == 46) {
    if (!delFlag) {
      delCount += 1;
      delFlag = true;
    }
  }
  else if (delFlag) {
    delFlag = false;
  }
}

function recordPause() {
  pauseCount += 1;
}

function getParameterByName(name) {
  name = name.replace(/[\[]/, "\\\[").replace(/[\]]/, "\\\]");
  var regex = new RegExp("[\\?&]" + name + "=([^&#]*)"),
  results = regex.exec(location.search);
  return results == null ? "" : decodeURIComponent(results[1].replace(/\+/g, " "));
}

function submitParameters() {
  logAction("submit");

  var assignmentId = document.getElementById("assignmentId");
  var hitId = document.getElementById("hitId");
  var workerId = document.getElementById("workerId");
  var prepareTime = document.getElementById("prepareTime");
  var taskTime = document.getElementById("taskTime");
  var numberOfOps = document.getElementById("numberOfOps");
  var numberOfPause = document.getElementById("numberOfPause");
  var numberOfDel = document.getElementById("numberOfDel");
  var imageWidth = document.getElementById("imageWidth");
  var imageHeight = document.getElementById("imageHeight");
  var eventHistory = document.getElementById("eventHistory");

  assignmentId.value = getParameterByName("assignmentId");
  hitId.value = getParameterByName("hitId");
  workerId.value = getParameterByName("workerId");

  prepareTime.value = annoStartTime - hitStartTime;
  taskTime.value = (new Date()).getTime() - annoStartTime;

  numberOfOps.value = opsCount;
  numberOfPause.value = pauseCount;
  numberOfDel.value = delCount;
  
  imageWidth.value = imgWidth;
  imageHeight.value = imgHeight;

  eventHistory.value = JSON.stringify(eventLogs);
}