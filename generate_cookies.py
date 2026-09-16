import datetime
import calendar

raw_data = """
__Secure-1PAPISID	NVmYjvjir79gx92b/A7Xx6ys-61MUyFFrc	.google.com	/	2027-10-13T03:56:44.379Z	51		✓				High	
__Secure-1PAPISID	NVmYjvjir79gx92b/A7Xx6ys-61MUyFFrc	.youtube.com	/	2027-10-13T04:08:35.833Z	51		✓				High	
__Secure-1PSID	g.a000CQmqwQ71vKpCq-m9XwIoY3a99mXbBE9aJBy0R4fW_wRSe9-fOrl-_4O53MsEmyQrLbKsHQACgYKAagSARcSFQHGX2Mikuu3w3Gwfleuq67_OpSTvBoVAUF8yKp6rmeevmuGtGgMPiugjk6y0076	.google.com	/	2027-10-13T03:56:44.381Z	167	✓	✓				High	
__Secure-1PSID	g.a000CQmqwXn0VgPCGMzjlrcFnNd0cIfQWxW98ZtC1LKYl8ZhdZCWI5-qWf432VIpGvujIP8bgAACgYKAS4SARcSFQHGX2Mi8zb4Eeh1oz3Gr8eca40vpxoVAUF8yKpBiVLlecKZhOUapcSlr-tb0076	.youtube.com	/	2027-10-13T04:08:35.834Z	167	✓	✓				High	
__Secure-1PSIDCC	AKEyXzWl_FiQFF1DTqM4lDrsHu8CAhIZFOzg18ytsv64njH6wiu6NTPAsAV_3M6U90jEwGeIoRY	.youtube.com	/	2027-09-16T05:18:44.975Z	91	✓	✓				High	
__Secure-1PSIDCC	AKEyXzVqQV5HwdSPy4tZWLofQujkPzt4xXZdnjQ7DlFRdfYX97lVUxBneZDuNp0m4qs2B5tp9eU	.google.com	/	2027-09-16T05:19:02.064Z	91	✓	✓				High	
__Secure-1PSIDTS	sidts-CjIBXMw41bsoKDH7PadQCEY1bOhHcMQzDtQI-ndba5jBwqbR-BmYcl1abPGm8szql_lKcxAA	.google.com	/	2027-09-16T05:16:25.428Z	94	✓	✓				High	
__Secure-1PSIDTS	sidts-CjUBXMw41Rd3IYbLesHuUnKn4HLRHZb7pZ9GUSv0iRB5IZvDfSNCs2KrISRAU-uuLRvmxA0MVhAA	.youtube.com	/	2027-09-16T05:17:39.409Z	98	✓	✓				High	
__Secure-3PAPISID	NVmYjvjir79gx92b/A7Xx6ys-61MUyFFrc	.google.com	/	2027-10-13T03:56:44.379Z	51		✓	None			High	
__Secure-3PAPISID	NVmYjvjir79gx92b/A7Xx6ys-61MUyFFrc	.youtube.com	/	2027-10-13T04:08:35.833Z	51		✓	None			High	
__Secure-3PSID	g.a000CQmqwXn0VgPCGMzjlrcFnNd0cIfQWxW98ZtC1LKYl8ZhdZCWH3lYp_7udS_XEAUcnmf2dQACgYKARkSARcSFQHGX2Mi8V9eRsOmgNfpv4SWMsVAlBoVAUF8yKqDJgCmIZmeo5Zjcrq8NVrs0076	.youtube.com	/	2027-10-13T04:08:35.834Z	167	✓	✓	None			High	
__Secure-3PSID	g.a000CQmqwQ71vKpCq-m9XwIoY3a99mXbBE9aJBy0R4fW_wRSe9-f1uqJb5_B9BJtCpGWmmHdXQACgYKAdwSARcSFQHGX2Mi5W-0UMveH-2byM0DC44b2xoVAUF8yKp5rfjcNerR_ik6H0Y-0sOD0076	.google.com	/	2027-10-13T03:56:44.381Z	167	✓	✓	None			High	
__Secure-3PSIDCC	AKEyXzUB3U2xnmrZtAPvRvy-u9kWdiYSCv-9bEHaBPyTkLJ4WKtRpgyl5oK5sNsbJ8qM57QNoCU	.youtube.com	/	2027-09-16T05:18:44.975Z	91	✓	✓	None			High	
__Secure-3PSIDCC	AKEyXzVAq71QbpNgjYGSxlam3QyJQm9L3fzaPqqxLzqR7o_7qmnf6IfCeHM3zVJHvkkqYcSA3Osu	.google.com	/	2027-09-16T05:19:02.064Z	92	✓	✓	None			High	
__Secure-3PSIDTS	sidts-CjUBXMw41Rd3IYbLesHuUnKn4HLRHZb7pZ9GUSv0iRB5IZvDfSNCs2KrISRAU-uuLRvmxA0MVhAA	.youtube.com	/	2027-09-16T05:17:39.409Z	98	✓	✓	None			High	
__Secure-3PSIDTS	sidts-CjIBXMw41bsoKDH7PadQCEY1bOhHcMQzDtQI-ndba5jBwqbR-BmYcl1abPGm8szql_lKcxAA	.google.com	/	2027-09-16T05:16:25.428Z	94	✓	✓	None			High	
__Secure-BUCKET	CJgC	.google.com	/	2026-12-24T10:35:21.443Z	19	✓	✓				Medium	
__Secure-ROLLOUT_TOKEN	CMe0uOKK6MC0tgEQl8_4_aunlQMY0aO3kp3wlgM%3D	.youtube.com	/	2027-03-14T09:03:17.566Z	64	✓	✓	None	https://youtube.com		Medium	
__Secure-YNID	21.YT=eSBLw27uoB3TWXaL2Udyw8eT_HxVWWasi7G6yWauk4LpSDFyp6WelJ90s6pNCwVJcDPd8G7aw4gTKnh7b4ucRdsCXKBRs9o7a4BsSZmVgG39EFWWmNy-nyBo2ejjd90WhBfd7njmN-w2Xn_QiXJR_qiRMsreIm3dmP44CeVjQbtvDGkFXFyaIfy8Qcd0ENpEFn2mnUBTGT5hNDUJf447-d3kFt2HFNPu4QwKwekf529oRhoWdjNeX0QDDOrHlKyAZoRjorH6R8MsOAYLQhzfwEc9RavXhS017PfWusOlXJgmfySQNURAYs-Se9uS2dXBLIi6xMFjmL8iy7voAcvU9A	.youtube.com	/	2027-03-14T09:03:17.566Z	361	✓	✓	None	https://youtube.com		Medium	
_gcl_au	1.1.892708785.1785837634	.youtube.com	/	2026-11-02T10:00:34.000Z	31						Medium	
AEC	AdJVEavkGsvBUNp2p1niJfykn6kTMEsGWiDqQSfaCCwTKer_BbWUusdUlQ	.google.com	/	2026-12-24T10:39:27.618Z	61	✓	✓	Lax			Medium	
APC	AdutNiZaJdnw6avxCpV37h1B1y1iup1mkqTn43tSWcx8x-PUeuRc3w	.doubleclick.net	/	2027-01-02T06:45:42.784Z	57		✓	None	https://youtube.com	✓	Medium	
"""

with open('/Users/hasibuzzaman/StudioProjects/musix-be/cookies.txt', 'w') as f:
    f.write("# Netscape HTTP Cookie File\n")
    f.write("# https://curl.haxx.se/rfc/cookie_spec.html\n")
    f.write("# This is a generated file!  Do not edit.\n\n")
    
    for line in raw_data.strip().split('\n'):
        parts = line.split('\t')
        if len(parts) >= 5:
            name = parts[0]
            value = parts[1]
            domain = parts[2]
            path = parts[3]
            expiry_str = parts[4]
            
            # Subdomains include flag
            include_subdomains = "TRUE" if domain.startswith(".") else "FALSE"
            
            # Secure flag (always true for __Secure)
            secure = "TRUE" if "Secure" in name or "✓" in line else "FALSE"
            
            # Expiration
            try:
                # Format: 2027-10-13T03:56:44.379Z
                dt = datetime.datetime.strptime(expiry_str, "%Y-%m-%dT%H:%M:%S.%fZ")
                expiry = str(calendar.timegm(dt.utctimetuple()))
            except Exception:
                expiry = "0"
            
            f.write(f"{domain}\\t{include_subdomains}\\t{path}\\t{secure}\\t{expiry}\\t{name}\\t{value}\\n")
