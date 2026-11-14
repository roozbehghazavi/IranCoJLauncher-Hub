ParticleDef()
{
	LifeTime()
	{
		keyf(0, 0.4)
	}

	GravityMul()
	{
		keyf(0, 0.6)
	}

	Drag()
	{
		keyf(0, 1.5)
	}

	WindInfluence()
	{
		keyf(0, 0)
	}

	Color()
	{
		keyv4(0, 1, 0.85, 0.6, 1)
		keyv4(0.4, 1, 0.5, 0.2, 0)
	}

	Size()
	{
		keyv(0, 4, 0.03, 0)
	}

	Trail()

	Material("Spark_particleADD.mat", "Spark_particleADD.mat")
}
