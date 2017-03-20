console.log("Start");
var socket = io.connect('http://' + document.domain + ':' + location.port + '/servo');

socket.on('connect', function(msg) {
    $('#operationSwitch').prop('disabled', false);
    $('#targetPosition').prop('disabled', false);

    console.log('[INFO] Socket connected.');
});

socket.on('disconnect', function(msg) {
    $('#operationSwitch').prop('disabled', true);
    $('#targetPosition').prop('disabled', true);
});

function sendPosition() {
    console.log('sendPosition, value: ' + $('#targetPosition').val());
    socket.emit('moveTo', $('#targetPosition').val());
}

function sendStop() {
    console.log('sendStop');
    socket.emit('stop');
}

function pullToLeft() {
    socket.emit('pullToLeft');
}

function pullToRight() {
    socket.emit('pullToRight');
}

function sendEnable() {
    console.log('sendEnable');
    socket.emit('enable');
}

function resetCenter() {
    socket.emit('resetCenter');
}

function toCenter() {
    $('#targetPosition').val(512).change();
}

function handleOperationSwitch(cb) {
    if (cb.checked)
        sendEnable();
    else
        sendStop();
}
