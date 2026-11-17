ParticleDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GravityMul()
	{
		randf(0, 1.5, 2)
	}

	Drag()
	{
		randf(0, 1, 2)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 1)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.86)
		keyv4(0.27, 0.55, 0.55, 0.55, 0.53)
		keyv4(0.47, 0.55, 0.55, 0.55, 0.25)
		keyv4(1, 0.55, 0.55, 0.55, 0.12)
		keyv4(1.6, 0.55, 0.55, 0.55, 0.1)
		keyv4(2, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		keyf(0, 34)
		keyf(0.42, 42)
		keyf(2, 68)
	}

	Align("on_start")

	AspectRatio()
	{
		randf(0, 1, 1)
	}

	Material("IRN_BloodClusterWS_particleBLEND.mat", "IRN_BloodClusterWS_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
