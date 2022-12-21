{
    "connections": [
        {
            "in_id": "{d14e48ab-0592-49cf-8d47-0b50e21ee7ad}",
            "in_index": 0,
            "out_id": "{b4d38fe9-3e72-4916-916a-c6871628ecc0}",
            "out_index": 0
        },
        {
            "in_id": "{b4d38fe9-3e72-4916-916a-c6871628ecc0}",
            "in_index": 0,
            "out_id": "{54835fbb-fe20-4b1f-bc32-efdd6f921f40}",
            "out_index": 0
        }
    ],
    "nodes": [
        {
            "id": "{ff443069-775a-4fa4-8788-0c4ad8e71d87}",
            "model": {
                "caption": "CanRawLogger #4",
                "directory": ".",
                "name": "CanRawLogger"
            },
            "position": {
                "x": 528,
                "y": 329
            }
        },
        {
            "id": "{d14e48ab-0592-49cf-8d47-0b50e21ee7ad}",
            "model": {
                "caption": "CanRawView #3",
                "name": "CanRawView",
                "scrolling": false,
                "viewColumns": [
                    {
                        "name": "time",
                        "vIdx": 1
                    },
                    {
                        "name": "id",
                        "vIdx": 2
                    },
                    {
                        "name": "dir",
                        "vIdx": 3
                    },
                    {
                        "name": "len",
                        "vIdx": 4
                    },
                    {
                        "name": "data",
                        "vIdx": 5
                    }
                ]
            },
            "position": {
                "x": 576,
                "y": 180
            }
        },
        {
            "id": "{54835fbb-fe20-4b1f-bc32-efdd6f921f40}",
            "model": {
                "caption": "CanRawSender #2",
                "content": [
                    {
                        "data": "1388000000000000",
                        "id": "0000014a",
                        "interval": "10",
                        "loop": true,
                        "remote": false,
                        "send": false
                    },
                    {
                        "data": "f254000000000000",
                        "id": "0000014a",
                        "interval": "10",
                        "loop": true,
                        "remote": false,
                        "send": false
                    },
                    {
                        "data": "204E409C81390270",
                        "id": "000001D0",
                        "interval": "10",
                        "loop": true,
                        "remote": false,
                        "send": false
                    }
                ],
                "name": "CanRawSender",
                "senderColumns": [
                    "Id",
                    "Data",
                    "Remote",
                    "Loop",
                    "Interval",
                    ""
                ],
                "sorting": {
                    "currentIndex": 0
                }
            },
            "position": {
                "x": 49,
                "y": 314
            }
        },
        {
            "id": "{b4d38fe9-3e72-4916-916a-c6871628ecc0}",
            "model": {
                "backend": "socketcan",
                "caption": "CanDevice #1",
                "configuration": "",
                "interface": "vcan0",
                "name": "CanDevice"
            },
            "position": {
                "x": 244,
                "y": 147
            }
        }
    ]
}
