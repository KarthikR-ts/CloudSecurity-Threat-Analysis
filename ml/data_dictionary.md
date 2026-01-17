# Data Dictionary - Microsoft GUIDE Dataset

Generated: 2026-01-14T19:41:42.890808

## Column Summary

| Column | Type | Category | Null % | Unique |
|--------|------|----------|--------|--------|
| Id | int64 | identifier | 0.0% | 730778 |
| OrgId | int16 | identifier | 0.0% | 5769 |
| IncidentId | int32 | identifier | 0.0% | 466151 |
| AlertId | int32 | identifier | 0.0% | 1265644 |
| Timestamp | object | temporal | 0.0% | 760944 |
| DetectorId | int16 | identifier | 0.0% | 8428 |
| AlertTitle | int32 | numerical | 0.0% | 86149 |
| Category | object | categorical | 0.0% | 20 |
| MitreTechniques | object | categorical | 57.46% | 1193 |
| IncidentGrade | category | target | 0.54% | 3 |
| ActionGrouped | object | categorical | 99.41% | 3 |
| ActionGranular | object | categorical | 99.41% | 16 |
| EntityType | object | categorical | 0.0% | 33 |
| EvidenceRole | category | identifier | 0.0% | 2 |
| DeviceId | int32 | identifier | 0.0% | 75826 |
| Sha256 | int32 | identifier | 0.0% | 106416 |
| IpAddress | int32 | numerical | 0.0% | 285957 |
| Url | int32 | numerical | 0.0% | 123252 |
| AccountSid | int32 | identifier | 0.0% | 358401 |
| AccountUpn | int32 | numerical | 0.0% | 530183 |
| AccountObjectId | int32 | identifier | 0.0% | 343516 |
| AccountName | int32 | numerical | 0.0% | 368250 |
| DeviceName | int32 | numerical | 0.0% | 114541 |
| NetworkMessageId | int32 | identifier | 0.0% | 375196 |
| EmailClusterId | float64 | identifier | 98.98% | 26474 |
| RegistryKey | int16 | identifier | 0.0% | 1341 |
| RegistryValueName | int16 | numerical | 0.0% | 525 |
| RegistryValueData | int16 | numerical | 0.0% | 699 |
| ApplicationId | int16 | identifier | 0.0% | 1728 |
| ApplicationName | int16 | numerical | 0.0% | 2681 |
| OAuthApplicationId | int16 | identifier | 0.0% | 703 |
| ThreatFamily | object | categorical | 99.21% | 1745 |
| FileName | int32 | numerical | 0.0% | 222085 |
| FolderPath | int32 | numerical | 0.0% | 87832 |
| ResourceIdName | int16 | identifier | 0.0% | 2309 |
| ResourceType | object | categorical | 99.93% | 25 |
| Roles | object | categorical | 97.71% | 10 |
| OSFamily | int8 | categorical | 0.0% | 6 |
| OSVersion | int8 | numerical | 0.0% | 58 |
| AntispamDirection | object | categorical | 98.14% | 5 |
| SuspicionLevel | category | categorical | 84.83% | 2 |
| LastVerdict | object | categorical | 76.52% | 5 |
| CountryCode | int16 | numerical | 0.0% | 236 |
| State | int16 | numerical | 0.0% | 1368 |
| City | int16 | numerical | 0.0% | 9342 |
