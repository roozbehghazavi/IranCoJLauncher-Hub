ParticleDef()
{
	LifeTime()
	{
		keyf(0, 3)
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
		keyv4(2.4, 0.55, 0.55, 0.55, 0.1)
		keyv4(3, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		keyf(0, 66)
		keyf(0.19, 74)
		keyf(3, 190)
	}

	Align("on_start")

	AspectRatio()
	{
		randf(0, 0.3, 0.4)
	}

	Material("IRN_BloodClusterWS_particleBLEND.mat", "IRN_BloodClusterWS_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
