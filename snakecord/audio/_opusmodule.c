#include "opus.h"

#include "Python.h"

#define SAMPLING_RATE 48000
#define CHANNELS 2
#define APPLICATION OPUS_APPLICATION_VOIP

typedef struct OpusEncoderObject {
    PyObject_HEAD
    OpusEncoder* encoder;
} OpusEncoderObject;

static PyObject* OpusEncoder_New(PyTypeObject* type, PyObject* args, PyObject* kwds);
static void OpusEncoder_Dealloc(OpusEncoderObject* self);
static PyObject* OpusEncoder_Encode(PyObject* self, PyObject* args);
static PyObject* OpusEncoder_SetBitrate(PyObject* self, PyObject* args);
static PyObject* OpusEncoder_SetFec(PyObject* self, PyObject* args);
static PyObject* OpusEncoder_SetPLP(PyObject* self, PyObject* args);


static PyMethodDef OpusEncoderMethods[] = {
    {"encode", OpusEncoder_Encode, METH_VARARGS, NULL},
    {"set_bitrate", OpusEncoder_SetBitrate, METH_VARARGS, NULL},
    {"set_fec", OpusEncoder_SetFec, METH_VARARGS, NULL},
    {"set_expected_plp", OpusEncoder_SetPLP, METH_VARARGS, NULL},
    {NULL, NULL, 0, NULL}
};

static PyTypeObject OpusEncoderType = {
    PyVarObject_HEAD_INIT(NULL, 0)
    .tp_name = "snakecord.OpusEncoder",
    .tp_itemsize = 0,
    .tp_flags = Py_TPFLAGS_DEFAULT,
    .tp_basicsize = sizeof(OpusEncoderObject),
    .tp_new = OpusEncoder_New,
    .tp_dealloc = (destructor)OpusEncoder_Dealloc,
    .tp_methods = OpusEncoderMethods
};

static PyObject* OpusSetException(int error, PyObject* ret)
{
    switch (error) {
    case OPUS_BAD_ARG:
        PyErr_SetString(PyExc_ValueError, "Opus received a bad argument");
    case OPUS_BUFFER_TOO_SMALL:
        PyErr_SetString(PyExc_ValueError, "Opus received a buffer that is too small");
    case OPUS_INTERNAL_ERROR:
        PyErr_SetString(PyExc_RuntimeError, "Opus ran into an internal error");
    case OPUS_INVALID_PACKET:
        PyErr_SetString(PyExc_ValueError, "Opus received an invalid packet");
    case OPUS_UNIMPLEMENTED:
        PyErr_SetString(PyExc_NotImplementedError, "Opus was asked to do something that is not implemented");
    case OPUS_INVALID_STATE:
        PyErr_SetString(PyExc_RuntimeError, "Opus was asked to do something with an invalid encoder/decoder");
    case OPUS_ALLOC_FAIL:
        PyErr_SetString(PyExc_MemoryError, "Opus failed to allocate memory");
    }
    return ret;
}

PyObject* OpusEncoder_New(PyTypeObject* type, PyObject* args, PyObject* kwds)
{
    int error;
    OpusEncoderObject* opus_encoder = (OpusEncoderObject*)PyType_GenericNew(type, args, kwds);
    opus_encoder->encoder = opus_encoder_create(SAMPLING_RATE, CHANNELS, APPLICATION, &error);
    return OpusSetException(error, (PyObject*)opus_encoder);
}

static PyObject* OpusEncoder_Encode(PyObject* self, PyObject* args)
{
    OpusEncoderObject* opus_encoder = (OpusEncoderObject*)self;

    PyObject* bytes = PyTuple_GetItem(args, 0);
    size_t size = PyBytes_Size(bytes);
    const opus_int16* pcm = (const opus_int16*)PyBytes_AsString(bytes);

    int frame_size = PyLong_AsLong(PyTuple_GetItem(args, 1));

    unsigned char* buffer = PyMem_Calloc(1, size); /* calloc 0s out the buffer */

    opus_int32 val;

    Py_BEGIN_ALLOW_THREADS
        val = opus_encode(opus_encoder->encoder, pcm, frame_size, buffer, (opus_int16)size);
    Py_END_ALLOW_THREADS

    if (val < 0) {
        return OpusSetException(val, NULL);
    }

    return PyBytes_FromStringAndSize(buffer, val);
}

PyObject* OpusEncoder_SetBitrate(PyObject* self, PyObject* args)
{
    OpusEncoderObject* opus_encoder = (OpusEncoderObject*)self;
    opus_int32 bitrate = PyLong_AsLong(PyTuple_GetItem(args, 0));
    opus_encoder_ctl(opus_encoder->encoder, OPUS_SET_BITRATE(bitrate));
    Py_RETURN_NONE;
}

PyObject* OpusEncoder_SetFec(PyObject* self, PyObject* args)
{
    OpusEncoderObject* opus_encoder = (OpusEncoderObject*)self;
    opus_int32 fec = PyObject_IsTrue(PyTuple_GetItem(args, 0));
    opus_encoder_ctl(opus_encoder->encoder, OPUS_SET_INBAND_FEC(fec));
    Py_RETURN_NONE;
}

PyObject* OpusEncoder_SetPLP(PyObject* self, PyObject* args)
{
    OpusEncoderObject* opus_encoder = (OpusEncoderObject*)self;
    opus_int32 plp = PyLong_AsLong(PyTuple_GetItem(args, 0));
    opus_encoder_ctl(opus_encoder->encoder, OPUS_SET_PACKET_LOSS_PERC(plp));
    Py_RETURN_NONE;
}

void OpusEncoder_Dealloc(OpusEncoderObject* self)
{
    opus_encoder_destroy(self->encoder);
    PyTypeObject* tp = Py_TYPE(self);
    tp->tp_free(self);
}

static PyMethodDef OpusMethods[] = {
    {NULL, NULL, 0, NULL}
};

static struct PyModuleDef opusmodule = {
    PyModuleDef_HEAD_INIT,
    "opus",
    NULL,
    -1,
    OpusMethods
};

PyMODINIT_FUNC PyInit_opus(void)
{
    PyObject* module = PyModule_Create(&opusmodule);
    PyTypeObject* encoder_type = &OpusEncoderType;
    Py_INCREF(encoder_type);
    if (PyType_Ready(encoder_type) < 0) {
        Py_DECREF(&OpusEncoderType);
        return NULL;
    }
    int status = PyModule_AddObject(module, "OpusEncoder", (PyObject*)encoder_type);
    if (status < 0) {
        return NULL;
    }
    return module;
}
