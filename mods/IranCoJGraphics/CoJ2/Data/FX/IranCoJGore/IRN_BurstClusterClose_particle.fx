ParticleDef()
{
	LifeTime()
	{
		keyf(0, 2)
	}

	GravityMul()
	{
		randf(0, 1, 1.4)
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
		keyf(0, 52)
		keyf(0.2, 64)
		keyf(2, 150)
	}

	Align("on_start")

	AspectRatio()
	{
		randf(0, 0.5, 0.6)
	}

	Material("IRN_BloodClusterWS_particleBLEND.mat", "IRN_BloodClusterWS_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
