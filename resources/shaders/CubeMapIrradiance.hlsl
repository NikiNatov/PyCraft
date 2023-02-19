#include "include/CommonConstants.hlsli"

static const uint NumSamples = 64 * 1024;
static const float InvNumSamples = 1.0 / float(NumSamples);

TextureCube EnvMap : register(t0);
SamplerState DefaultSampler : register(s0);

RWTexture2DArray<float4> IrradianceMap : register(u0);

float RadicalInverse_VdC(uint bits)
{
	bits = (bits << 16u) | (bits >> 16u);
	bits = ((bits & 0x55555555u) << 1u) | ((bits & 0xAAAAAAAAu) >> 1u);
	bits = ((bits & 0x33333333u) << 2u) | ((bits & 0xCCCCCCCCu) >> 2u);
	bits = ((bits & 0x0F0F0F0Fu) << 4u) | ((bits & 0xF0F0F0F0u) >> 4u);
	bits = ((bits & 0x00FF00FFu) << 8u) | ((bits & 0xFF00FF00u) >> 8u);
	return float(bits) * 2.3283064365386963e-10;
}

float2 SampleHammersley(uint i)
{
	return float2(i * InvNumSamples, RadicalInverse_VdC(i));
}

float3 SampleHemisphere(float u1, float u2)
{
	const float u1p = sqrt(max(0.0, 1.0 - u1 * u1));
	return float3(cos(TwoPI * u2) * u1p, sin(TwoPI * u2) * u1p, u1);
}

float3 GetSamplingVector(uint3 ThreadID)
{
	float outputWidth, outputHeight, outputDepth;
	IrradianceMap.GetDimensions(outputWidth, outputHeight, outputDepth);

	float2 st = ThreadID.xy / float2(outputWidth, outputHeight);
	float2 uv = 2.0 * float2(st.x, 1.0 - st.y) - 1.0;

	float3 ret = float3(0.0, 0.0, 0.0);
	switch (ThreadID.z)
	{
		case 0: ret = float3(1.0, uv.y, -uv.x); break;
		case 1: ret = float3(-1.0, uv.y, uv.x); break;
		case 2: ret = float3(uv.x, 1.0, -uv.y); break;
		case 3: ret = float3(uv.x, -1.0, uv.y); break;
		case 4: ret = float3(uv.x, uv.y, 1.0); break;
		case 5: ret = float3(-uv.x, uv.y, -1.0); break;
	}
	return normalize(ret);
}

void ComputeBasisVectors(const float3 N, out float3 S, out float3 T)
{
	T = cross(N, float3(0.0, 1.0, 0.0));
	T = lerp(cross(N, float3(1.0, 0.0, 0.0)), T, step(Epsilon, dot(T, T)));

	T = normalize(T);
	S = normalize(cross(N, T));
}

float3 TangentToWorld(const float3 v, const float3 N, const float3 S, const float3 T)
{
	return S * v.x + T * v.y + N * v.z;
}

[numthreads(32, 32, 1)]
void CSMain(uint3 ThreadID : SV_DispatchThreadID)
{
	float3 N = GetSamplingVector(ThreadID);

	float3 S, T;
	ComputeBasisVectors(N, S, T);

	float3 irradiance = 0.0;
	for (uint i = 0; i < NumSamples; i++) 
	{
		float2 u = SampleHammersley(i);
		float3 Li = TangentToWorld(SampleHemisphere(u.x, u.y), N, S, T);
		float cosTheta = max(0.0, dot(Li, N));

		irradiance += 2.0 * EnvMap.SampleLevel(DefaultSampler, Li, 0).rgb * cosTheta;
	}
	irradiance /= float(NumSamples);

	IrradianceMap[ThreadID] = float4(irradiance, 1.0);
}