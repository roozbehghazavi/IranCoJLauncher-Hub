ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.7)
	}

	GravityMul()
	{
		randf(0, 0.4, 0.6)
	}

	Drag()
	{
		randf(0, 1, 2)
	}

	Color()
	{
		keyv4(0, 0.55, 0.55, 0.55, 0.5)
		keyv4(0.17, 0.55, 0.55, 0.55, 0.43)
		keyv4(0.27, 0.55, 0.55, 0.55, 0.265)
		keyv4(0.47, 0.55, 0.55, 0.55, 0.125)
		keyv4(0.56, 0.55, 0.55, 0.55, 0.05)
		keyv4(0.7, 0.55, 0.55, 0.55, 0)
	}

	Size()
	{
		keyf(0, 20)
		keyf(0.7, 60)
	}

	Align("on_start")

	AspectRatio()
	{
		randf(0, 0.6, 0.6)
	}

	Material("IRN_BloodSplatWS_particleBLEND.mat", "IRN_BloodSplatWS_particleBLEND.mat")

	TexMultiRect(2, 2, 4)
	TexPlayMode("random_once", 1)
}
